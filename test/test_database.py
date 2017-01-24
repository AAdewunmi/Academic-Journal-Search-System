from os import path
import unittest

from comp62521.database import database

class TestDatabase(unittest.TestCase):

    def setUp(self):
        dir, _ = path.split(__file__)
        self.data_dir = path.join(dir, "..", "data")

    def test_read(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        self.assertEqual(len(db.publications), 1)

    def test_read_invalid_xml(self):
        db = database.Database()
        self.assertFalse(db.read(path.join(self.data_dir, "invalid_xml_file.xml")))

    def test_read_missing_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "missing_year.xml")))
        self.assertEqual(len(db.publications), 0)

    def test_read_missing_title(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "missing_title.xml")))
        # publications with missing titles should be added
        self.assertEqual(len(db.publications), 1)

    def test_get_average_authors_per_publication(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-1.xml")))
        _, data = db.get_average_authors_per_publication(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.3, places=1)
        _, data = db.get_average_authors_per_publication(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 2, places=1)
        _, data = db.get_average_authors_per_publication(database.Stat.MODE)
        self.assertEqual(data[0], [2])

    def test_get_average_publications_per_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        _, data = db.get_average_publications_per_author(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 1.5, places=1)
        _, data = db.get_average_publications_per_author(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 1.5, places=1)
        _, data = db.get_average_publications_per_author(database.Stat.MODE)
        self.assertEqual(data[0], [0, 1, 2, 3])

    def test_get_average_publications_in_a_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-3.xml")))
        _, data = db.get_average_publications_in_a_year(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.5, places=1)
        _, data = db.get_average_publications_in_a_year(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 3, places=1)
        _, data = db.get_average_publications_in_a_year(database.Stat.MODE)
        self.assertEqual(data[0], [3])

    def test_get_average_authors_in_a_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-4.xml")))
        _, data = db.get_average_authors_in_a_year(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.8, places=1)
        _, data = db.get_average_authors_in_a_year(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 3, places=1)
        _, data = db.get_average_authors_in_a_year(database.Stat.MODE)
        self.assertEqual(data[0], [0, 2, 4, 5])
        # additional test for union of authors
        self.assertEqual(data[-1], [0, 2, 4, 5])

    def test_get_publication_summary(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publication_summary()
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data[0]), 6,
            "incorrect number of columns in data")
        self.assertEqual(len(data), 2,
            "incorrect number of rows in data")
        self.assertEqual(data[0][1], 1,
            "incorrect number of publications for conference papers")
        self.assertEqual(data[1][1], 2,
            "incorrect number of authors for conference papers")

    def test_get_average_authors_per_publication_by_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "three-authors-and-three-publications.xml")))
        header, data = db.get_average_authors_per_publication_by_author(database.Stat.MEAN)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 3,
            "incorrect average of number of conference papers")
        self.assertEqual(data[0][1], 1.5,
            "incorrect mean journals for author1")
        self.assertEqual(data[1][1], 2,
            "incorrect mean journals for author2")
        self.assertEqual(data[2][1], 1,
            "incorrect mean journals for author3")

    def test_get_publications_by_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publications_by_author(None)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 2,
            "incorrect number of authors")
        self.assertEqual(data[0][-3], 1,
            "incorrect total")

    def test_get_publications_by_author_givenNone_returnsUnorderedList(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple ordered.xml")))
        header, data = db.get_publications_by_author(None)
        self.assertEqual("AUTHORA B", data[0][0],
            "Authora B should be first in the list")
        self.assertEqual("AUTHORB A", data[1][0],
            "Authorb A should be 2nd in the list")
        self.assertEqual("AUTHORC C", data[2][0],
            "Authorc C should be last in the list")

    def test_get_publications_by_author_givenDesc_returnsDescOrderedList(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple ordered.xml")))
        header, data = db.get_publications_by_author("Desc")
        self.assertEqual("AUTHORB A", data[0][0],
            "Authorb A should be first in the list")
        self.assertEqual("AUTHORA B", data[1][0],
            "Authora B should be 2nd in the list")
        self.assertEqual("AUTHORC C", data[2][0],
            "Authorc C should be last in the list")

    def test_get_publications_by_author_givenAsc_returnsAscOrderedList(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple ordered.xml")))
        header, data = db.get_publications_by_author("Asc")
        self.assertEqual("AUTHORC C", data[0][0],
            "Authorc C should be first in the list")
        self.assertEqual("AUTHORA B", data[1][0],
            "Authora B should be 2nd in the list")
        self.assertEqual("AUTHORB A", data[2][0],
            "Authorb A should be last in the list")

    def test_get_publications_by_author_newColumnAdded(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple ordered.xml")))
        header, data = db.get_publications_by_author(None)
        self.assertEqual("Number of Sole Author Papers", header[-1],
            "Last item in the header should be Number of Sole Author Papers")

    def test_get_publications_by_author_givenNoSoleAuthors_showsColumnAs0(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple sole authors.xml")))
        header, data = db.get_publications_by_author("Desc")
        self.assertEqual(0, data[1][-1],
            "Should be 0 sole authors for Author B")

    def test_get_publications_by_author_given1SoleAuthorForAuthorA_showsColumnAs1(self):
            db = database.Database()
            self.assertTrue(db.read(path.join(self.data_dir, "simple sole authors.xml")))
            header, data = db.get_publications_by_author("Desc")
            self.assertEqual(1, data[0][-1],
                "Should be 1 sole authors for author A")
            self.assertEqual(1, data[2][-1],
                "Should be 1 sole authors for author C")

    def test_get_publications_by_author_given2SoleAuthorForAuthorD_showsColumnAs2(self):
            db = database.Database()
            self.assertTrue(db.read(path.join(self.data_dir, "simple sole authors.xml")))
            header, data = db.get_publications_by_author("Desc")
            self.assertEqual(2, data[3][-1],
                "Should be 2 sole authors for author D")

    def test_get_publications_by_author_newColumnAddedForFirstAuthor(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple first authors.xml")))
        header, data = db.get_publications_by_author(None)
        self.assertEqual("Number of First Author Papers", header[-3],
            "Second to last item in the header should be Number of First Author Papers")

    def test_get_publications_by_author_givenAuthorWithNoFirstAuthorPublications_showsColumnAs0(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple first authors.xml")))
        header, data = db.get_publications_by_author(None)
        self.assertEqual(0, data[1][-3],
                "Should be 0 first author publications for Author2")

    def test_get_publications_by_author_givenAuthorWith1FirstAuthorPublication_showsColumnAs1(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple first authors.xml")))
        header, data = db.get_publications_by_author(None)
        self.assertEqual(1, data[2][-3],
                "Should be 1 first author publication for Author3")

    def test_get_publications_by_author_newColumnAddedForLastAuthor(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple first authors.xml")))
        header, data = db.get_publications_by_author(None)
        self.assertEqual("Number of Last Author Papers", header[-2],
            "Second to last item in the header should be Number of Last Author Papers")

    def test_getAuthorWithFirstNamedPublications_givenAuthorWithNoFirstAuthorPublications_showsColumnAs0(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple first authors.xml")))
        data = db.getAuthorsWithFirstNamedPublications()
        self.assertEqual(0, sum(data["Author2"].values()),
                "Should be 0 first author publications for Author2")

    def test_getAuthorWithFirstNamedPublications_givenAuthorWith1FirstAuthorPublication_returns1ForAuthor(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple first authors.xml")))
        data = db.getAuthorsWithFirstNamedPublications()
        self.assertEqual(1, sum(data["Author3"].values()),
                "Should be 1 first author publication for Author3")

    def test_getAuthorWithFirstNamedPublications_givenAuthorWith2FirstAuthorPublication_returns2ForAuthor(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple first authors.xml")))
        data = db.getAuthorsWithFirstNamedPublications()
        self.assertEqual(2, sum(data["Author1"].values()),
                "Should be 2 first author publication for Author1")

    def test_getAuthorWithLastNamedPublications_givenAuthorWithNoLastAuthorPublications_showsColumnAs0(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple first authors.xml")))
        data = db.getAuthorWithLastNamedPublications()
        self.assertEqual(0, sum(data["Author2"].values()),
                "Should be 0 last author publications for Author2")

    def test_getAuthorWithLastNamedPublications_givenAuthorWith1LastAuthorPublications_showsColumnAs1(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple first authors.xml")))
        data = db.getAuthorWithLastNamedPublications()
        self.assertEqual(1, sum(data["Author4"].values()),
                "Should be 1 last author publications for Author4")

    def test_getAuthorWithLastNamedPublications_givenAuthorWith2LastAuthorPublications_showsColumnAs2(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple first authors.xml")))
        data = db.getAuthorWithLastNamedPublications()
        self.assertEqual(2, sum(data["Author1"].values()),
                "Should be 2 last author publications for Author1")

    def test_getAuthorsOverallPublications_givenAuthorWith1OverallPublications_showsColumnAs1(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple first authors.xml")))
        data = db.getAuthorWithLastNamedPublications()
        self.assertEqual(1, sum(data["Author9"].values()),
                "Should be 1 overall publications for Author9")

    def getAuthorPublicationsBreakdown_givenAuthor1_returnsCorrectValuesForEach(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple first authors.xml")))
        data = db.getAuthorPublicationsBreakdown("Author1")
        self.assertEqual(2, data["Book"][2],
                "Should be 2 first author books for Author1")
        self.assertEqual(2, data["Book"][3],
                "Should be 2 last author books for Author1")
        self.assertEqual(1, data["Journal"][2],
                "Should be 2 first author books for Author1")

    def getAuthorPublicationsBreakdown_givenNonExistentAuthor_returns0(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple first authors.xml")))
        data = db.getAuthorPublicationsBreakdown("Author11")
        self.assertEqual(0, data["Book"][2],
                "Should be 2 first author books for Author1")
        self.assertEqual(0, data["Book"][3],
                "Should be 2 last author books for Author1")
        self.assertEqual(0, data["Journal"][2],
                "Should be 2 first author books for Author1")

    def test_getAuthorsWithSoleNamedPublications_given1SoleAuthor_returns1(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple first authors.xml")))
        data = db.getAuthorsWithSoleNamedPublications()
        self.assertEqual(1, sum(data["Author1"].values()),
                "Should be 1 overall publications for Author1")

    def test_get_average_publications_per_author_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_average_publications_per_author_by_year(database.Stat.MEAN)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 1,
            "incorrect number of rows")
        self.assertEqual(data[0][0], 9999,
            "incorrect year in result")

    def test_get_publications_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publications_by_year()
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 1,
            "incorrect number of rows")
        self.assertEqual(data[0][0], 9999,
            "incorrect year in result")

    def test_get_author_totals_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_author_totals_by_year()
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 1,
            "incorrect number of rows")
        self.assertEqual(data[0][0], 9999,
            "incorrect year in result")
        self.assertEqual(data[0][1], 2,
            "incorrect number of authors in result")

    def test_search_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        headers, author = db.get_author_stats("Robert Stevens")
        self.assertEqual(author, [u'Robert Stevens', 79, 52, 0, 3, 134, 14, 55, 0])



if __name__ == '__main__':
    unittest.main()
