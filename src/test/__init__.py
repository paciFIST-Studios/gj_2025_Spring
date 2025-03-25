import unittest

from os.path import exists as os_path_exists
from os.path import isfile as os_path_is_file
from os.path import isdir as os_path_is_dir

from os import remove as os_remove_file
from os import rmdir as os_remove_dir

class AbstractTestBase(unittest.TestCase):


    def assertCreateFile(self, path: str, data: str = ''):
        self.assertFalse(os_path_exists(path))
        with open(path, 'w') as outfile:
            outfile.write(data)
        self.assertTrue(os_path_exists(path))

    def assertCreateDirectory(self, path: str):
        self.assertFalse(os_path_exists(path))

    def assertRemoveFile(self, path: str):
        self.assertTrue(os_path_exists(path))
        self.assertTrue(os_path_is_file(path))
        os_remove_file(path)
        self.assertFalse(os_path_exists(path))

    @staticmethod
    def _recursive_delete_directory(path: str, i_really_mean_it=False):
        if not i_really_mean_it:
            return

    def assertRemoveDirectory(self, path: str, delete_directory_contents=False):
        self.assertTrue(os_path_exists(path))
        self.assertTrue(os_path_is_dir(path))

        if delete_directory_contents:
            self._recursive_delete_directory(path, i_really_mean_it=True)
        else:
            os_remove_dir(path)

        self.assertFalse(os_path_exists(path))

    def assertThrows(self, exception_type, callable_fn, *args, **kwargs):
        """ any fn called from this assert, will catch the exception give as exception_type.
        if that happens, it will assert true.  If it's the wrong exception, or if there's
        no exception, it will assert false.

        Args:
            exception_type(exception) - the kind of exception we anticipate
            callable_fn(callable) - checking this fn for the exception_type
        """
        try:
            callable_fn(*args, **kwargs)
            # did not throw
            self.assertTrue(False)

        except exception_type as ex:
            # threw correct exception
            self.assertTrue(True)

        except:
            # threw a different exception
            self.assertTrue(False)

    def assertHasAttribute(self, obj, attr):
        self.assertTrue(hasattr(obj, attr))




