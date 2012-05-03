from utils import *
import unittest

class TestUtilFunctions(unittest.TestCase):
    
    def test_exercise_cmp(self):
        #Basic
        self.assertTrue(exercise_cmp("1","2") < 0 )
        self.assertTrue(exercise_cmp("1","1") == 0 )
        self.assertTrue(exercise_cmp("2","1") > 0 )
        # 12 should be larger than 2
        self.assertTrue(exercise_cmp("12","2") > 0 )
        #now with multiple places
        self.assertTrue(exercise_cmp("1.1","1.0") > 0 )
        self.assertTrue(exercise_cmp("2"  ,"1.1") > 0 )
        self.assertTrue(exercise_cmp("2.1","2"  ) > 0 )
        self.assertTrue(exercise_cmp("2.1","2.1") ==0 )
        self.assertTrue(exercise_cmp("2.12","2.2")> 0 )
        #Non numerical should come last
        self.assertTrue(exercise_cmp("2.OPTIONAL" ,"2.0"  ) > 0 )
        self.assertTrue(exercise_cmp("2.OPTIONAL" ,"2.OPTIONAL"  ) == 0 )
if __name__ == '__main__':
    unittest.main()

