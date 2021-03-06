import unittest

from au.com.gegroup.tests.base.spark_test_case import SparkTestCase
from au.com.gegroup.ts.graphframes_reader import GraphFramesReader
from au.com.gegroup.ts.writer import Writer

__author__ = 'topsykretts'


class GraphFramesReadWriteTest(SparkTestCase):
    """
    Test read / write from GraphFramesReader class
    """
    def test_filodb_in_memory_write(self):
        """
        A dataframe is constructed and written to in-memory filodb
        [Note: the dataframe is not sorted]
        :return:
        """
        ts = [
            (1001, "site1", "level1", "Site ACU 1", "ACU-1_RAT", 20.52),
            (1000, "site1", "level1", "Site ACU 1", "ACU-1_SAT", 23.52),
            (1002, "site1", "level1", "Site ACU 1", "ACU-1_SAT", 21.52),
            (1003, "site1", "level1", "Site ACU 1", "ACU-1_SAT", 18.52)
        ]
        """
        testing writing a dataset to filodb in-memory
        :return:
        """
        print("converting to dataframe")
        df = self.sqlContext.createDataFrame(ts, ["time", "siteRef", "levelRef", "equipRef", "pointName", "value"])
        df.show()
        print("Writing to filodb")
        writer = Writer(df, "test_iot_gf_rwt_1", "time,equipRef,pointName")
        writer.mode("overwrite").write()

# --------------------------------------------------------------------------------------------------------------------

    def test_read_from_filodb(self):
        """
        The dataset written in filodb is read back.
        [Note: Though the order of schema isn't preserved, the read dataframe is sorted.]
        """
        print("reading from filodb")
        reader = GraphFramesReader(self.sqlContext, "test_iot_gf_rwt_1", "test_iot_rwt_1")
        reader.get_df().show()
        print("vertices")
        reader.graph_df.vertices.show(5)
        print("edges")
        reader.graph_df.edges.show()

# --------------------------------------------------------------------------------------------------------------------

    def test_read_from_dataframe(self):
        """
        Provision to read timeseries directly from dataframe
        """
        schema = ["datetime", "siteRef", "levelRef", "equipRef", "pointName", "value"]
        ts = [
            (1000, "site1", "level1", "Site ACU 1", "ACU-1_SAT", 23.52),
            (1001, "site1", "level1", "Site ACU 1", "ACU-1_RAT", 20.52),
            (1002, "site1", "level1", "Site ACU 1", "ACU-1_SAT", 21.52),
            (1003, "site1", "level1", "Site ACU 1", "ACU-1_RAT", 18.52),
            (1000, "site1", "level1", "Site ACU 1", "ACU-1_SATSP", 15.6),
            (1003, "site1", "level1", "Site ACU 1", "ACU-1_SATSP", 16.7)
        ]
        # create dataframe
        input_df = self.sqlContext.createDataFrame(ts, schema)
        # read from dataframe with load_filter neglecting SATSP
        reader = GraphFramesReader(self.sqlContext, input_df, "test_iot_gf_rwt_2", "siteRef = 'site1'").has_timestamp(False)
        # read sat points based on metadata
        sat_ts = reader.metadata("supply and air and sensor and levelRef = 'level1'").is_sorted(False).read()
        sat_ts.show()
        # assert only ACU-1_SAT points are read
        assert (sat_ts.select("pointName").distinct().collect()[0][0]) == "ACU-1_SAT"

if __name__ == '__main__':
    unittest.main()
