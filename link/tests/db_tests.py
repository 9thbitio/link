import unittest
import os
from link.wrappers import DBConnectionWrapper
from mock import Mock, MagicMock

class TestDBConnectionWrapper(unittest.TestCase):
    """
    Test that we are wrapping DB connections correctly
    """
    def setUp(self):
        self.cw = DBConnectionWrapper()
        #create a fake connection that is a mock as well
        self.cw._wrapped = Mock()
        self.cw.execute = MagicMock()
        self.cw.execute.return_value = MagicMock()
        self.cw.execute.return_value.fetchall = MagicMock()
        self.cw.description = MagicMock()
    
    def test_select_dataframe(self):
        return_val = [(1,2), (3,4)]
        headers = [['Col1'], ['col2']]
        self.cw.execute.return_value.fetchall.return_value = return_val
        self.cw.execute.return_value.description = headers
        query = 'my select statement'
        results = self.cw.select_dataframe(query)
        #check to see that the headers match but all lower case
        self.assertEquals([d for d in results.columns],
                          [c[0].lower() for c in headers]) 
    
    def test_select(self):
        query = 'my select statement'
        results = self.cw.select(query)
        expected = ((1,2), (3,4))
        results._data = expected
        self.assertEquals(query, results.query)
        self.assertEquals(results.data, expected) 


if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
                   exit=False)
 
#class TestSqliteConnection(unittest.TestCase):
    
    #TEST_DB = 'test_sqlite.db'

    #def setUp(self):
        ## if it already exists then just remove it
        #if os.path.exists(TEST_DB):
            #os.remove(TEST_DB)
        ##create a new connection to the db
        #self.connection = SqlLiteDBConnectionWrapper(path=TEST_DB)

    #def test_execute(self):
        #self.connection.execute("""create table test_table 
                                #(col1 int, col2 int)""")
        
        #self.assertTrue(True)

    #def test_false(self):
        #self.assertTrue(True)

