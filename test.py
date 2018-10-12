import unittest


class CommandLineTest(unittest.TestCase):
    def run_cmd(self, cmd):
        import subprocess
        output = subprocess.check_output(cmd, shell=True)
        return output.decode()

    def assertCommand(self, cmd, expected):
        output = self.run_cmd(cmd)
        if output != expected:
            from pprint import pprint
            pprint(list(map(repr, output.splitlines())))
            pprint(list(map(repr, expected.splitlines())))
            raise AssertionError

    def test_a1b1_col2_c_s_b_s_w_F(self):
        self.assertCommand('python -m tinycal -3 --col 2 -w', open('output').read())


if __name__=='__main__':
    output = CommandLineTest('__new__').run_cmd('python -m tinycal')
    print(output)
