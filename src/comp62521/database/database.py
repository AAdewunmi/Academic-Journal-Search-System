from comp62521.statistics import average
import itertools
import numpy as np
from xml.sax import handler, make_parser, SAXException

PublicationType = [
    "Conference Paper", "Journal", "Book", "Book Chapter"]

class Publication:
    CONFERENCE_PAPER = 0
    JOURNAL = 1
    BOOK = 2
    BOOK_CHAPTER = 3

    def __init__(self, pub_type, title, year, authors):
        self.pub_type = pub_type
        self.title = title
        if year:
            self.year = int(year)
        else:
            self.year = -1
        self.authors = authors

class Author:
    def __init__(self, name):
        self.name = name

class Stat:
    STR = ["Mean", "Median", "Mode"]
    FUNC = [average.mean, average.median, average.mode]
    MEAN = 0
    MEDIAN = 1
    MODE = 2

class Database:
    def read(self, filename):
        self.publications = []
        self.authors = []
        self.author_idx = {}
        self.min_year = None
        self.max_year = None

        handler = DocumentHandler(self)
        parser = make_parser()
        parser.setContentHandler(handler)
        infile = open(filename, "r")
        valid = True
        try:
            parser.parse(infile)
        except SAXException as e:
            valid = False
            print "Error reading file (" + e.getMessage() + ")"
        infile.close()

        for p in self.publications:
            if self.min_year == None or p.year < self.min_year:
                self.min_year = p.year
            if self.max_year == None or p.year > self.max_year:
                self.max_year = p.year

        return valid

    def get_all_authors(self):
        return self.author_idx.keys()

    def get_coauthor_data(self, start_year, end_year, pub_type):
        coauthors = {}
        for p in self.publications:
            if ((start_year == None or p.year >= start_year) and
                (end_year == None or p.year <= end_year) and
                (pub_type == 4 or pub_type == p.pub_type)):
                for a in p.authors:
                    for a2 in p.authors:
                        if a != a2:
                            try:
                                coauthors[a].add(a2)
                            except KeyError:
                                coauthors[a] = set([a2])
        def display(db, coauthors, author_id):
            return "%s (%d)" % (db.authors[author_id].name, len(coauthors[author_id]))

        header = ("Author", "Co-Authors")
        data = []
        for a in coauthors:
            data.append([ display(self, coauthors, a),
                ", ".join([
                    display(self, coauthors, ca) for ca in coauthors[a] ]) ])

        return (header, data)

    def get_average_authors_per_publication(self, av):
        header = ("Conference Paper", "Journal", "Book", "Book Chapter", "All Publications")

        auth_per_pub = [[], [], [], []]

        for p in self.publications:
            auth_per_pub[p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ func(auth_per_pub[i]) for i in np.arange(4) ] + [ func(list(itertools.chain(*auth_per_pub))) ]
        return (header, data)

    def get_average_publications_per_author(self, av):
        header = ("Conference Paper", "Journal", "Book", "Book Chapter", "All Publications")

        pub_per_auth = np.zeros((len(self.authors), 4))

        for p in self.publications:
            for a in p.authors:
                pub_per_auth[a, p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ func(pub_per_auth[:, i]) for i in np.arange(4) ] + [ func(pub_per_auth.sum(axis=1)) ]
        return (header, data)

    def get_average_publications_in_a_year(self, av):
        header = ("Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        ystats = np.zeros((int(self.max_year) - int(self.min_year) + 1, 4))

        for p in self.publications:
            ystats[p.year - self.min_year][p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ func(ystats[:, i]) for i in np.arange(4) ] + [ func(ystats.sum(axis=1)) ]
        return (header, data)

    def get_average_authors_in_a_year(self, av):
        header = ("Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        yauth = [ [set(), set(), set(), set(), set()] for _ in range(int(self.min_year), int(self.max_year) + 1) ]

        for p in self.publications:
            for a in p.authors:
                yauth[p.year - self.min_year][p.pub_type].add(a)
                yauth[p.year - self.min_year][4].add(a)

        ystats = np.array([ [ len(S) for S in y ] for y in yauth ])

        func = Stat.FUNC[av]

        data = [ func(ystats[:, i]) for i in np.arange(5) ]
        return (header, data)

    def get_publication_summary_average(self, av):
        header = ("Details", "Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        pub_per_auth = np.zeros((len(self.authors), 4))
        auth_per_pub = [[], [], [], []]

        for p in self.publications:
            auth_per_pub[p.pub_type].append(len(p.authors))
            for a in p.authors:
                pub_per_auth[a, p.pub_type] += 1

        name = Stat.STR[av]
        func = Stat.FUNC[av]

        data = [
            [name + " authors per publication"]
                + [ func(auth_per_pub[i]) for i in np.arange(4) ]
                + [ func(list(itertools.chain(*auth_per_pub))) ],
            [name + " publications per author"]
                + [ func(pub_per_auth[:, i]) for i in np.arange(4) ]
                + [ func(pub_per_auth.sum(axis=1)) ] ]
        return (header, data)

    def get_publication_summary(self):
        header = ("Details", "Conference Paper",
            "Journal", "Book", "Book Chapter", "Total")

        plist = [0, 0, 0, 0]
        alist = [set(), set(), set(), set()]

        for p in self.publications:
            plist[p.pub_type] += 1
            for a in p.authors:
                alist[p.pub_type].add(a)
        
        # create union of all authors
        ua = alist[0] | alist[1] | alist[2] | alist[3]

        data = [
            ["Number of publications"] + plist + [sum(plist)],
            ["Number of authors"] + [ len(a) for a in alist ] + [len(ua)] ]
        return (header, data)

    def get_average_authors_per_publication_by_author(self, av):
        header = ("Author", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "All publications")

        astats = [ [[], [], [], []] for _ in range(len(self.authors)) ]
        for p in self.publications:
            for a in p.authors:
                astats[a][p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ [self.authors[i].name]
            + [ func(L) for L in astats[i] ]
            + [ func(list(itertools.chain(*astats[i]))) ]
            for i in range(len(astats)) ]
        return (header, data)


    def get_publications_by_author(self, sortOrder):
        header = ("Author", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "Total", "Number of First Author Papers", "Number of Last Author Papers", "Number of Sole Author Papers")

        astats = [ [0, 0, 0, 0] for _ in range(len(self.authors)) ]
        
        firstAuthors = self.getAuthorsWithFirstNamedPublications()
        lastAuthors = self.getAuthorWithLastNamedPublications()
        soleAuthors = self.getAuthorsWithSoleNamedPublications()
        
        for p in self.publications:         
            for a in p.authors:
                astats[a][p.pub_type] += 1       

        data = [ [self.authors[i].name] + astats[i] + [sum(astats[i])] + [sum(firstAuthors[self.authors[i].name].values())] 
                    + [sum(lastAuthors[self.authors[i].name].values())] + [sum(soleAuthors[self.authors[i].name].values())]
                    for i in range(len(astats)) ]

        if (sortOrder is not None):
            if (sortOrder == "Asc"):
                data.sort(key=lambda authorName: authorName[0].split(" ")[-1], reverse=True)
            elif (sortOrder == "Desc"):
                data.sort(key=lambda authorName: authorName[0].split(" ")[-1], reverse=False)

        return (header, data)

    def getAuthorsWithFirstNamedPublications(self):
        firstAuthors = {}

        for publication in self.publications:
            authorName = self.authors[publication.authors[0]].name

            if (len(publication.authors) > 1):
            
                firstAuthorByPubType = {}

                #If the authors not in the outer dictionary, add them with the above empty dictionary
                if (authorName not in firstAuthors):
                    firstAuthors[authorName] = firstAuthorByPubType
                else:
                    #Otherwise retrieve the existing dictionary
                    firstAuthorByPubType = firstAuthors[authorName]

                #Get this publication type as a string
                publicationTypeString = PublicationType[publication.pub_type]
				
                # If Author does not exist put a 0, otherwise sum 1
                firstAuthorByPubType[publicationTypeString] = firstAuthorByPubType.get(publicationTypeString,0) + 1

        for author in self.authors:
            if (author.name not in firstAuthors):
                firstAuthors[author.name] = {}

        return firstAuthors
        

    def getAuthorWithLastNamedPublications(self):
        lastAuthors = {}

        for publication in self.publications:
            authorName = self.authors[publication.authors[-1]].name

            if (len(publication.authors) > 1):
            
                lastAuthorByPubType = {}

                #If the authors not in the outer dictionary, add them with the above empty dictionary
                if (authorName not in lastAuthors):
                    lastAuthors[authorName] = lastAuthorByPubType
                else:
                    #Otherwise retrieve the existing dictionary
                    lastAuthorByPubType = lastAuthors[authorName]

                #Get this publication type as a string
                publicationTypeString = PublicationType[publication.pub_type]
                
				# If Author does not exist put a 0, otherwise sum 1
                lastAuthorByPubType[publicationTypeString] = lastAuthorByPubType.get(publicationTypeString,0) + 1

        for author in self.authors:
            if (author.name not in lastAuthors):
                lastAuthors[author.name] = {}

        return lastAuthors
    
    #Returns a dictionary of authors containing a dictionary of publication type with the count
    def getAuthorsWithSoleNamedPublications(self):
        soleAuthors = {}

        for publication in self.publications:
            authorName = self.authors[publication.authors[0]].name

            #single author publications only
            if (len(publication.authors) == 1):
                #This is the inner dictionary to contain the publication type with count
                soleAuthorByPubType = {}

                #If the authors not in the outer dictionary, add them with the above empty dictionary
                if (authorName not in soleAuthors):
                    soleAuthors[authorName] = soleAuthorByPubType
                else:
                    #Otherwise retrieve the existing dictionary
                    soleAuthorByPubType = soleAuthors[authorName]

                #Get this publication type as a string
                publicationTypeString = PublicationType[publication.pub_type]
                
				# If Author does not exist put a 0, otherwise sum 1
                soleAuthorByPubType[publicationTypeString] = soleAuthorByPubType.get(publicationTypeString,0) + 1            
                
        #Fill any authors / publication types not in the map with a 0
        for author in self.authors:
            if (author.name not in soleAuthors):
                soleAuthors[author.name] = {}
        
        return soleAuthors

    def getAuthorsOverallPublications(self):
        overall = {}

        for publication in self.publications:
            for a in publication.authors: 
                authorName = self.authors[a].name
                            
                overallByPubType = {}

                #If the authors not in the outer dictionary, add them with the above empty dictionary
                if (authorName not in overall):
                    overall[authorName] = overallByPubType
                else:
                    #Otherwise retrieve the existing dictionary
                    overallByPubType = overall[authorName]

                #Get this publication type as a string
                publicationTypeString = PublicationType[publication.pub_type]
                
                # If Author does not exist put a 0, otherwise sum 1
                overallByPubType[publicationTypeString] = overallByPubType.get(publicationTypeString,0) + 1

        for author in self.authors:
            if (author.name not in overall):
                overall[author.name] = {}

        return overall

    def getPublicationBreakDown(self, publicationType):
        #Get all sole, first and last authors broken down by publication type
        soleAuthors = self.getAuthorsWithSoleNamedPublications()
        firstAuthors = self.getAuthorsWithFirstNamedPublications()
        lastAuthors = self.getAuthorWithLastNamedPublications()
        overall = self.getAuthorsOverallPublications()
        
        
        #Store the data in a map of author name with the count of the sole author publications / first author / last author etc
        data = {}

        for author in self.authors:
            # If the person isnt in the map, add them
            if (author.name not in data):
                #data[author.name] = [0,0,0]
                data[author.name] = [0,0,0,0]

            # get the value for this authors number of sole, first amd last author by publication
            data[author.name][0] = soleAuthors[author.name].get(publicationType,0)
            data[author.name][1] = firstAuthors[author.name].get(publicationType,0)
            data[author.name][2] = lastAuthors[author.name].get(publicationType,0)
            data[author.name][3] = overall[author.name].get(publicationType,0)

        headers = ("Author", "Number of Sole Author Publications", "Number of First Author Publications", "Number of Last Author Publications", "Number of Overall Publications")

        return (headers, data)

    def get_average_authors_per_publication_by_year(self, av):
        header = ("Year", "Conference papers",
            "Journals", "Books",
            "Book chapers", "All publications")

        ystats = {}
        for p in self.publications:
            try:
                ystats[p.year][p.pub_type].append(len(p.authors))
            except KeyError:
                ystats[p.year] = [[], [], [], []]
                ystats[p.year][p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ [y]
            + [ func(L) for L in ystats[y] ]
            + [ func(list(itertools.chain(*ystats[y]))) ]
            for y in ystats ]
        return (header, data)

    def get_publications_by_year(self):
        header = ("Year", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "Total")

        ystats = {}
        for p in self.publications:
            try:
                ystats[p.year][p.pub_type] += 1
            except KeyError:
                ystats[p.year] = [0, 0, 0, 0]
                ystats[p.year][p.pub_type] += 1

        data = [ [y] + ystats[y] + [sum(ystats[y])] for y in ystats ]
        return (header, data)

    def get_average_publications_per_author_by_year(self, av):
        header = ("Year", "Conference papers",
            "Journals", "Books",
            "Book chapers", "All publications")

        ystats = {}
        for p in self.publications:
            try:
                s = ystats[p.year]
            except KeyError:
                s = np.zeros((len(self.authors), 4))
                ystats[p.year] = s
            for a in p.authors:
                s[a][p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ [y]
            + [ func(ystats[y][:, i]) for i in np.arange(4) ]
            + [ func(ystats[y].sum(axis=1)) ]
            for y in ystats ]
        return (header, data)

    def get_author_totals_by_year(self):
        header = ("Year", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "Total")

        ystats = {}
        for p in self.publications:
            try:
                s = ystats[p.year][p.pub_type]
            except KeyError:
                ystats[p.year] = [set(), set(), set(), set()]
                s = ystats[p.year][p.pub_type]
            for a in p.authors:
                s.add(a)
        data = [ [y] + [len(s) for s in ystats[y]] + [len(ystats[y][0] | ystats[y][1] | ystats[y][2] | ystats[y][3])]
            for y in ystats ]
        return (header, data)

    def add_publication(self, pub_type, title, year, authors):
        if year == None or len(authors) == 0:
            print "Warning: excluding publication due to missing information"
            print "    Publication type:", PublicationType[pub_type]
            print "    Title:", title
            print "    Year:", year
            print "    Authors:", ",".join(authors)
            return
        if title == None:
            print "Warning: adding publication with missing title [ %s %s (%s) ]" % (PublicationType[pub_type], year, ",".join(authors))
        idlist = []
        for a in authors:
            try:
                idlist.append(self.author_idx[a])
            except KeyError:
                a_id = len(self.authors)
                self.author_idx[a] = a_id
                idlist.append(a_id)
                self.authors.append(Author(a))
        self.publications.append(
            Publication(pub_type, title, year, idlist))
        if (len(self.publications) % 100000) == 0:
            print "Adding publication number %d (number of authors is %d)" % (len(self.publications), len(self.authors))

        if self.min_year == None or year < self.min_year:
            self.min_year = year
        if self.max_year == None or year > self.max_year:
            self.max_year = year

    def _get_collaborations(self, author_id, include_self):
        data = {}
        for p in self.publications:
            if author_id in p.authors:
                for a in p.authors:
                    try:
                        data[a] += 1
                    except KeyError:
                        data[a] = 1
        if not include_self:
            del data[author_id]
        return data

    def get_coauthor_details(self, name):

        author_id = self.author_idx[name]
        print author_id, name
        data = self._get_collaborations(author_id, True)
        return [ (self.authors[key].name, data[key])
            for key in data ]


    def get_network_data(self):
        na = len(self.authors)

        nodes = [ [self.authors[i].name, -1] for i in range(na) ]
        links = set()
        for a in range(na):
            collab = self._get_collaborations(a, False)
            nodes[a][1] = len(collab)
            for a2 in collab:
                if a < a2:
                    links.add((a, a2))
        return (nodes, links)

    def get_author_stats(self, name):
        headers  = ["The number of conference papers:","The number of journal articles:","The number of books:", "The number of book chapters:", "The overall number of publication:", "Number of First Author Papers", "Number of Last Author Papers", "Number of Sole Author Papers:"]

        if name != "":
             data = self.get_publications_by_author(None)             
             for author_stats in data[1]:
                  if name.lower() == author_stats[0].lower():
                     return headers, author_stats
                 
        
        return "",""

    def getAuthorPublicationsBreakdown(self, authorName):
        data = {}

        if authorName != "":
            #Get all sole, first and last authors broken down by publication type
            soleAuthors = self.getAuthorsWithSoleNamedPublications()
            firstAuthors = self.getAuthorsWithFirstNamedPublications()
            lastAuthors = self.getAuthorWithLastNamedPublications()
            overall = self.getAuthorsOverallPublications()

            for pubType in PublicationType:
                data[pubType] = [soleAuthors.get(authorName,{}).get(pubType,0), 
                                    firstAuthors.get(authorName,{}).get(pubType,0),
                                    lastAuthors.get(authorName,{}).get(pubType,0),
                                    overall.get(authorName,{}).get(pubType,0)]

            headers = ("Publication Type", "Number of Sole Author Publications", "Number of First Author Publications", 
                        "Number of Last Author Publications", "Number of Overall Publications")

            return (headers, data)

        return "", data

class DocumentHandler(handler.ContentHandler):
    TITLE_TAGS = [ "sub", "sup", "i", "tt", "ref" ]
    PUB_TYPE = {
        "inproceedings":Publication.CONFERENCE_PAPER,
        "article":Publication.JOURNAL,
        "book":Publication.BOOK,
        "incollection":Publication.BOOK_CHAPTER }

    def __init__(self, db):
        self.tag = None
        self.chrs = ""
        self.clearData()
        self.db = db

    def clearData(self):
        self.pub_type = None
        self.authors = []
        self.year = None
        self.title = None

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, name, attrs):
        if name in self.TITLE_TAGS:
            return
        if name in DocumentHandler.PUB_TYPE.keys():
            self.pub_type = DocumentHandler.PUB_TYPE[name]
        self.tag = name
        self.chrs = ""

    def endElement(self, name):
        if self.pub_type == None:
            return
        if name in self.TITLE_TAGS:
            return
        d = self.chrs.strip()
        if self.tag == "author":
            self.authors.append(d)
        elif self.tag == "title":
            self.title = d
        elif self.tag == "year":
            self.year = int(d)
        elif name in DocumentHandler.PUB_TYPE.keys():
            self.db.add_publication(
                self.pub_type,
                self.title,
                self.year,
                self.authors)
            self.clearData()
        self.tag = None
        self.chrs = ""

    def characters(self, chrs):
        if self.pub_type != None:
            self.chrs += chrs
