import pytest

from catalog_validation.exceptions import ValidationErrors
from catalog_validation.utils import WANTED_FILES_IN_ITEM_VERSION
from catalog_validation.validation import (
    validate_train_structure, validate_questions_yaml, validate_catalog_item, validate_catalog_item_version,
)


@pytest.mark.parametrize('train_path,should_work', [
    ('/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts', True),
    ('/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts/', False),

])
def test_validate_train_structure(train_path, should_work):
    if should_work:
        assert validate_train_structure(train_path) is None
    else:
        with pytest.raises(ValidationErrors):
            validate_train_structure(train_path)


@pytest.mark.parametrize('test_yaml,should_work', [
    (
        '''
            groups:
              - name: "Machinaris Configuration"
                description: "Configure timezone for machianaris"

            portals:
              web_portal:
                protocols:
                  - "http"
                host:
                  - "$node_ip"
                ports:
                  - "$variable-machinaris_ui_port"

            questions:
              - variable: timezone
                label: "Configure timezone"
                group: "Machinaris Configuration"
                description: "Configure timezone for machianaris"
        ''',
        True
    ),
    (
        '''
            groups:
              - name: "Machinaris Configuration"
                description: "Configure timezone for machianaris"

            portals:
              web_portal:
                protocols: {}
                host: {}
                ports: {}

            questions:
              - variable: timezone
                label: "Configure timezone"
                group: "Machinaris Configuration"
                description: "Configure timezone for machianaris"
        ''',
        False
    ),
    (
        '''
        questions:
          - variable: timezone
            label: "Configure timezone"
            group: "Machinaris Configuration"
            description: "Configure timezone for machianaris"
        ''',
        False
    ),
    (
        '''
            groups:
              - name: "Machinaris Configuration"
                description: "Configure timezone for machianaris"

            questions:
              - variable: timezone
                label: "Configure timezone"
                group: "Machinaris Configuration"
                description: "Configure timezone for machianaris"
        ''',
        True
    ),
    (
        '''
            groups:
              - name: "Machinaris Configuration"
                description: "Configure timezone for machianaris"

            questions:
              - variable: timezone
                label: "Network"
                group: "Machinaris Network Configuration"
                description: "Configure timezone for machianaris"

        ''',
        False
    ),

])
def test_validate_questions_yaml(mocker, test_yaml, should_work):
    open_file_data = mocker.mock_open(read_data=test_yaml)
    mocker.patch('builtins.open', open_file_data)
    mocker.patch('catalog_validation.validation.validate_question', return_value=None)
    if should_work:
        assert validate_questions_yaml(None, 'charts.machinaris.versions.1.1.13.questions_configuration') is None
    else:
        with pytest.raises(ValidationErrors):
            validate_questions_yaml(None, 'charts.machinaris.versions.1.1.13.questions_configuration')


@pytest.mark.parametrize('catalog_item_path,test_yaml,should_work', [
    (
        '/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts/machinaris',
        '''
         categories:
           - storage
           - crypto
         icon_url: https://raw.githubusercontent.com/guydavis/machinaris/main/web/static/machinaris.png
        ''',
        True
    ),
    (
        '/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts/machinaris',
        '''
            icon_url: https://raw.githubusercontent.com/guydavis/machinaris/main/web/static/machinaris.png
        ''',
        False
    ),
])
def test_validate_catalog_item(mocker, catalog_item_path, test_yaml, should_work):
    mocker.patch('os.path.isdir', side_effect=[True, True, False])
    mocker.patch('os.listdir', return_value=['1.1.13', 'item.yaml'])
    open_file_data = mocker.mock_open(read_data=test_yaml)
    mocker.patch('builtins.open', open_file_data)
    mocker.patch('catalog_validation.validation.validate_catalog_item_version', return_value=None)
    if not should_work:
        with pytest.raises(ValidationErrors):
            validate_catalog_item(catalog_item_path, 'charts.machinaris')
    else:
        assert validate_catalog_item(catalog_item_path, 'charts.machinaris') is None


@pytest.mark.parametrize('chart_yaml,should_work', [
    (
        '''
        name: storj
        version: 1.0.4
        ''',
        True
    ),
    (
        '''
        name: storj
        version: 1.0.0
        ''',
        False
    ),
    (
        '''
        name: storj_s
        version: 1.0.0
        ''',
        False
    )
])
def test_validate_catalog_item_version(mocker, chart_yaml, should_work):
    mocker.patch('os.listdir', return_value=WANTED_FILES_IN_ITEM_VERSION)
    mocker.patch('os.path.exists', return_value=True)
    open_file = mocker.mock_open(read_data=chart_yaml)
    mocker.patch('builtins.open', open_file)
    mocker.patch('catalog_validation.validation.validate_questions_yaml', return_value=None)
    if should_work:
        assert validate_catalog_item_version(
            '/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts/storj/1.0.4',
            'charts.storj.versions.1.0.4') is None
    else:
        with pytest.raises(ValidationErrors):
            validate_catalog_item_version(
                '/mnt/mypool/ix-applications/catalogs/github_com_truenas_charts_git_master/charts/storj/1.0.4',
                'charts.storj.versions.1.0.4'
            )