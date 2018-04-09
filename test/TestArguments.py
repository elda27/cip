import unittest
import os.path
import sys

path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(path)

import arguments

class ParserTest(unittest.TestCase):
    def testParse(self):
        cases = [
            { "load": ([ "v1", "v2", "v3" ], {}) },
            { "cv.load": ([ "v1", "v2", "v3" ], { "kw":"this", "any":"value" } ), "ls.save": ([ "v1", "v2" ], {}) },
            { "uni": ([], {}), "save": ([ "v1", "v2" ], {}) },
        ]

        for case in cases:
            args = []
            for key, value in case.items():
                args.append(key + ":")
                args.extend(value[0])
                args.extend([ k + "=" + v for k, v in value[1].items() ])
            
            parser = arguments.ArgumentsParser()
            parser.parse(args)
            tokens = parser.tokens()
            for token in tokens:
                self.assertIn(token.command(), case)
                cur_case = case[token.command()]
                cur_args = cur_case[0]
                cur_kwargs = cur_case[1]
                self.assertTrue(all([lhs == rhs for lhs, rhs in zip(cur_args, token.args())]), '{} != {}'.format(cur_args, token.args())) 
                for kw, va in token.kwargs().items():
                    self.assertIn(kw, cur_kwargs)
                    self.assertEqual(va, cur_kwargs[kw])

if __name__ == '__main__':
    unittest.main()
