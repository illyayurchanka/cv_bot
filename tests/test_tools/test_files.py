from src.tools.files import read_file, write_file

class TestReadFile:
    def test_reads_file_at_provided_path(self, tmp_path):
        file = tmp_path / "test_cv.tex"
        file.write_text("\\documentclass{article}\\n\\begin{document}Hello\\end{document}")

        result = read_file(path=str(file))
        assert "\\documentclass{article}" in result

    def test_reads_file_at_provided_file_path(self, tmp_path):
        file = tmp_path / "test_cv.tex"
        file.write_text("content via file_path")

        result = read_file(file_path=str(file))
        assert result == "content via file_path"

    def test_path_takes_precedence_over_default(self, tmp_path):
        file = tmp_path / "custom.tex"
        file.write_text("custom content")

        result = read_file(path=str(file))
        assert result == "custom content"

    def test_returns_error_for_missing_file(self, tmp_path):
        missing = tmp_path / "nonexistent.tex"
        result = read_file(path=str(missing))
        assert result.startswith("error reading file:")

    def test_truncates_to_10000_chars(self, tmp_path):
        file = tmp_path / "long.tex"
        file.write_text("A" * 15_000)

        result = read_file(path=str(file))
        assert len(result) == 10_000

    def test_no_args_reads_default_cv(self):
        result = read_file()
        assert isinstance(result, str)


class TestWriteFile:
    def test_writes_to_provided_path(self, tmp_path):
        file = tmp_path / "output.tex"

        result = write_file(content="hello world", path=str(file))

        assert file.read_text() == "hello world"
        assert "successfully wrote" in result
        assert str(file) in result

    def test_writes_to_provided_file_path(self, tmp_path):
        file = tmp_path / "output2.tex"

        result = write_file(content="via file_path", file_path=str(file))

        assert file.read_text() == "via file_path"
        assert "successfully wrote" in result

    def test_path_takes_precedence_over_default(self, tmp_path):
        file = tmp_path / "custom_output.tex"

        write_file(content="custom", path=str(file))

        assert file.read_text() == "custom"

    def test_returns_error_for_invalid_path(self):
        result = write_file(content="data", path="/nonexistent_dir_xyz/file.tex")
        assert result.startswith("error writing file:")

    def test_creates_parent_directories_not_needed(self, tmp_path):
        file = tmp_path / "subdir" / "output.tex"
        result = write_file(content="data", path=str(file))
        assert result.startswith("error writing file:")

    def test_overwrites_existing_file(self, tmp_path):
        file = tmp_path / "existing.tex"
        file.write_text("old content")

        write_file(content="new content", path=str(file))

        assert file.read_text() == "new content"

    def test_no_args_writes_to_default_cv(self):
        result = write_file(content="test")
        assert isinstance(result, str)
