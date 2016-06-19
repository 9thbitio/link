import unittest
import os
from link.wrappers import DBConnectionWrapper, SqliteDBConnectionWrapper
from link.wrappers import DBCursorWrapper
from mock import Mock, MagicMock
from link.tests import *

class TestDBConnectionWrapper(unittest.TestCase):
    """
    Test that we are wrapping DB connections correctly
    """
    def setUp(self):
        self.cw = DBConnectionWrapper()

    def set_db_return(self, values, columns=None, query=None):
        cursor =  Mock()
        cursor.fetchall.return_value = values
        cursor.description = columns or []

        self.cw._wrapped = Mock()
        db_response = DBCursorWrapper(cursor, query).execute()

        self.cw.execute = Mock()
        self.cw.execute.return_value = db_response


    def test_select_dataframe(self):
        return_val = [(1,2), (3,4)]
        columns = [['Col1'], ['col2']]
        self.set_db_return(return_val, columns)

        query = 'my select statement'
        results = self.cw.select_dataframe(query)
        #check to see that the headers match but all lower case
        self.assertEquals([d for d in results.columns],
                          [c[0].lower() for c in columns]) 
    
    def test_select(self):
        query = 'my select statement'

        return_val = ((1,2), (3,4))

        self.set_db_return(return_val, query=query)

        results = self.cw.select(query)
        self.assertEquals(query, results.query)
        self.assertEquals(results.data, return_val) 


class TestSqliteConnection(unittest.TestCase):

    db_path_with_default = tst_db_path('test_db.db')

    def setUp(self):
        self.cw_db = SqliteDBConnectionWrapper(path = self.db_path_with_default)
        self.cw_no_chunk = SqliteDBConnectionWrapper(path = self.db_path_with_default)
    
    def test_db_created(self):
        # don't change this table please
        data = self.cw_db.select('select * from test_table where column = 1').data
        self.assertEquals(data[0][0], 1)
        self.assertTrue(self.cw._wrapped == None)

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
 
