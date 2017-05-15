import unittest
import os
from link.wrappers import DBConnectionWrapper, SqliteDBConnectionWrapper, DBCursorWrapper
from mock import Mock, MagicMock
from link.tests import *

class TestDBConnectionWrapper(unittest.TestCase):
    """
    Test that we are wrapping DB connections correctly
    """
    def setUp(self):
        self.cw = DBConnectionWrapper()
        #create a fake connection that is a mock as well
        self.cw._wrapped = Mock()
        self.cw.execute = MagicMock()

        self.cw.execute.return_value = DBCursorWrapper(MagicMock())
        self.cw.execute.return_value.fetchall = MagicMock()
        self.cw.description = MagicMock()
    
    def test_select_dataframe(self):
        return_val = [(1,2), (3,4)]
        headers = [['Col1'], ['col2']]
        self.cw.execute.return_value._wrapped.fetchall.return_value = return_val
        self.cw.execute.return_value._wrapped.description = headers
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

    def check_chunk(self):
        self.cw.chunks = {'this_chunk':True}
        self.assertTrue(self.cw.chunk('this_chunk'))


class TestSqliteConnection(unittest.TestCase):

    db_path = tst_db_path('test_db')
    db_path_with_default = tst_db_path('test_db.db')

    def setUp(self):
        self.cw = SqliteDBConnectionWrapper(path = self.db_path, chunked = True)
        self.cw_db = SqliteDBConnectionWrapper(path = self.db_path_with_default, chunked = True)
        self.cw_no_chunk = SqliteDBConnectionWrapper(path = self.db_path_with_default)
    
    def test_db_created(self):
        # don't change this table please
        data = self.cw_db.select('select * from test_table where column = 1').data
        self.assertEquals(data[0][0], 1)
        self.assertTrue(self.cw._wrapped == None)

    def test_db_chunk_created(self):
        # don't change this table please
        data = self.cw_db.select('select * from test_table_chunk where column = 1',
                                 chunk_name = 'my_chunk.db').data
        self.assertEquals(data[0][0], 1)
        data = self.cw_db.select('select * from test_table_chunk where column = 1',
                                 chunk_name = 'my_chunk.db').data
        self.assertEquals(data[0][0], 1)

    def test_db_created(self):
        # don't change this table please
        data = self.cw_no_chunk.select('select * from test_table where column = 1').data
        self.assertEquals(data[0][0], 1)
        self.assertRaises(Exception, self.cw_no_chunk.select, 
                          'select * from test_table_chunk where column = 1',chunk_name = 'my_chunk.db')


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

