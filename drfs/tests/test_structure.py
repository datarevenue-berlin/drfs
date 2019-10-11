
def test_local_file_structure(tmpdir):
    with SettingsOverride(ROOT=str(tmpdir)):
        FSTRUCT = FileStructure(
            DATA_DIR=('data',),
            TEMPLATE=('DATA_DIR', '{}.txt'),
            )
        FSTRUCT['SINGLE_FILE'] = ('DATA_DIR', 'somefile.md')
        assert isinstance(FSTRUCT['ROOT'], Path)
        assert str(FSTRUCT.format('TEMPLATE', 'test')) == str(tmpdir.join(
            'data', 'test.txt'))
        assert FSTRUCT['SINGLE_FILE'] == FSTRUCT['DATA_DIR'].joinpath('somefile.md')
        correct_repr = """test_local_file_structure0
└── data [DATA_DIR]
    ├── {}.txt [TEMPLATE]
    └── somefile.md [SINGLE_FILE]
    """.splitlines()

        for correct, produced in zip(correct_repr, str(FSTRUCT).splitlines()):
            assert correct == produced


def test_remote_file_structure():
    with SettingsOverride(ROOT='s3://datarevenue/project_name'):
        FSTRUCT = FileStructure(
            DATA_DIR=('data',),
            TEMPLATE=('data', '{}.txt'),
        )
        FSTRUCT['SINGLE_FILE'] = ('data', 'somefile.md')
        assert isinstance(FSTRUCT['ROOT'], RemotePath)
        assert isinstance(FSTRUCT['SINGLE_FILE'], RemotePath)
        assert isinstance(FSTRUCT.format('TEMPLATE', 'blah'), RemotePath)
        assert str(FSTRUCT['ROOT']) == 's3://datarevenue/project_name'
        assert str(FSTRUCT.format('TEMPLATE', 'blah')) == \
            's3://datarevenue/project_name/data/blah.txt'


def test_substitution():
    with SettingsOverride(ROOT='s3://root'):
        PATH = FileStructure(
            {
                'EVAL':         ('models', ),
                'RAW':          ('raw', ),
                'CS_IN':            ('RAW', 'clickstream.csv'),
                'PROCESSED':    ('processed', ),
                'CS_OUT':           ('PROCESSED', 'clickstream.pickle'),

            }
        )
        assert str(PATH['ROOT']) == 's3://root'
        assert str(PATH['EVAL']) == 's3://root/models'
        assert str(PATH['RAW']) == 's3://root/raw'
        assert str(PATH['CS_IN']) == 's3://root/raw/clickstream.csv'
        assert str(PATH['PROCESSED']) == 's3://root/processed'
        assert str(PATH['CS_OUT']) == 's3://root/processed/clickstream.pickle'
