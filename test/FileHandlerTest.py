from unittest import TestCase
from unittest import mock
from src.FileHandler import FileHandler


class FileHandlerTest(TestCase):

    def test__is_file_relevant(self):

        file_handler = FileHandler()

        self.assertFalse(file_handler._is_file_relevant(file_path="C:\ a /b/_{}/ :te-~%³.txt"))

        for is_file in [False, True]:
            with mock.patch("pathlib.Path.is_file", return_value=is_file) as mock_is_file:
                self.assertEqual(is_file, file_handler._is_file_relevant("C://a.txt"))