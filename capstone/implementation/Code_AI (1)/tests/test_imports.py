def test_package_files_compile():
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[1]
    assert (root / "backend" / "main.py").exists()
    assert (root / "frontend" / "app.py").exists()
