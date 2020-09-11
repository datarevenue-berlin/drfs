from drfs import Tree, P, DRPath


class Structure(Tree):
    class data(Tree):
        file: P = DRPath("{name}.csv")


def test_independent_instances():
    structure1 = Structure("/tmp")
    structure2 = Structure("/tmp/dir/")

    assert str(structure1.data.file.format(name="file1")) == "/tmp/data/file1.csv"
    assert str(structure2.data.file.format(name="file1")) == "/tmp/dir/data/file1.csv"
