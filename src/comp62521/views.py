from comp62521 import app
from database import database
from flask import (render_template, request)

def format_data(data):
    fmt = "%.2f"
    result = []
    for item in data:
        if type(item) is list:
            result.append(", ".join([ (fmt % i).rstrip('0').rstrip('.') for i in item ]))
        else:
            result.append((fmt % item).rstrip('0').rstrip('.'))
    return result

@app.route("/averages")
def showAverages():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"averages"}
    args['title'] = "Averaged Data"
    args["description"] = "This page displays data on the average number of authors per publication."
    tables = []
    headers = ["Average", "Conference Paper", "Journal", "Book", "Book Chapter", "All Publications"]
    averages = [ database.Stat.MEAN, database.Stat.MEDIAN, database.Stat.MODE ]
    tables.append({
        "id":1,
        "title":"Average Authors per Publication",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_authors_per_publication(i)[1])
                for i in averages ] })
    tables.append({
        "id":2,
        "title":"Average Publications per Author",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_publications_per_author(i)[1])
                for i in averages ] })
    tables.append({
        "id":3,
        "title":"Average Publications in a Year",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_publications_in_a_year(i)[1])
                for i in averages ] })
    tables.append({
        "id":4,
        "title":"Average Authors in a Year",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_authors_in_a_year(i)[1])
                for i in averages ] })

    args['tables'] = tables
    return render_template("averages.html", args=args)

@app.route("/coauthors")
def showCoAuthors():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    PUB_TYPES = ["Conference Papers", "Journals", "Books", "Book Chapters", "All Publications"]
    args = {"dataset":dataset, "id":"coauthors"}
    args["title"] = "Co-Authors"
    args["description"] = "This page displays detailed information on co-author research collaboration for individual authors. The data can be displayed as an annual statistic or between the years 1980 to 2013. In addition, data is displayed according to (a) all publications, (b) conference paper, (c) journal, (d) book and (e) book chapter."

    start_year = db.min_year
    if "start_year" in request.args:
        start_year = int(request.args.get("start_year"))

    end_year = db.max_year
    if "end_year" in request.args:
        end_year = int(request.args.get("end_year"))

    pub_type = 4
    if "pub_type" in request.args:
        pub_type = int(request.args.get("pub_type"))

    args["data"] = db.get_coauthor_data(start_year, end_year, pub_type)
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_type"] = pub_type
    args["min_year"] = db.min_year
    args["max_year"] = db.max_year
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_str"] = PUB_TYPES[pub_type]
    return render_template("coauthors.html", args=args)

@app.route("/")
def showStatisticsMenu():
    dataset = app.config['DATASET']
    args = {"dataset":dataset}
    return render_template('statistics.html', args=args)

@app.route("/statisticsdetails/<status>")
def showPublicationSummary(status):
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":status}

    if (status == "publication_summary"):
        args["title"] = "Publication Summary"
        args["data"] = db.get_publication_summary()
        args["description"] = "This page displays a summary of all research publications, whether collaborative or otherwise. This information is broken down into number of publications and number of authors within the following categories (a) Conference Paper, (b) Journal Paper, (c) Books and (d) Book Chapter."

    if (status == "publication_author"):
        args["title"] = "Author Publication"
        args["description"] = "This page displays the aggregate statistics for individual authors, categorised into (a) number of conference papers, (b) number of journals, (c) number of books, and (d) number of book chapters. In addition, data on the (a) number of first author papers, (b) number of last author papers and (c) number of sole author paper is provided for each author."

        if (request.args.get("sortAuthor") is not None):
            sortOrder = (request.args.get("sortAuthor"))
            args["data"] = db.get_publications_by_author(sortOrder)
        else:
            args["data"] = db.get_publications_by_author(None)

    if (status == "publication_year"):
        args["title"] = "Publication by Year"
        args["data"] = db.get_publications_by_year()
        args["description"] = "This page gives an overview of the number of research publications on a year by year basis, and is displayed according to (a) number of conference papers, (b) number of journals, (c) number of books, (d) number of book chapters."

    if (status == "author_year"):
        args["title"] = "Author by Year"
        args["data"] = db.get_author_totals_by_year()
        args["description"] = "This page displays information regarding the publications made by authors on an annual basis, and is displayed according to (a) number of conference papers, (b) number of journals, (c) number of books, (d) number of books and (e) number of book chapters."

    return render_template('statistics_details.html', args=args)

@app.route("/authorstats")
def showAuthorStatistics():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"searchauthor"}
    args["title"] = "Search Author"
    args["description"] = "This page allows the user to type in a name, and returns all the statistics for that author, according to the following categories (a) number of conference papers, (b) number of journal articles, (c) number of books, (d) number of book chapters, (e) overall number of publication, (f) number of first Author, (g) number of last author papers and (h) number of sole author papers."
    
    author_name = ""
    if "author_name" in request.args:
        author_name = request.args.get("author_name")
 
    args["data"] = db.get_author_stats(author_name)
    args["pub_split"] = db.getAuthorPublicationsBreakdown(author_name)
    args["set"] = set
    return render_template("authorstats.html", args=args)


@app.route("/conferencePapersBreakdown")
def conferencePapersBreakdown():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset}

    #Title
    args["title"] = "Conference Papers Breakdown"
        
    #Get data, specify which publication type when calling the method
    args["data"] = db.getPublicationBreakDown("Conference Paper")
    args["description"] = "This page displays a breakdown of data for individual authors on conference paper publications according to (a) number of sole author publications, (b) number of first author publications, (c) number of last author publications and (d) number of overall publications."

    return render_template('conferencePapersBreakdown.html', args=args)
	
	
@app.route("/journalBreakdown")
def journalBreakdown():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset}

    #Title
    args["title"] = "Journal Breakdown"
        
    #Get data, specify which publication type when calling the method
    args["data"] = db.getPublicationBreakDown("Journal")
    args["description"] = "This page displays a breakdown of data for individual authors on journal paper publications according to (a) number of sole author publications, (b) number of first author publications, (c) number of last author publications and (d) number of overall publications."
        
    return render_template('journalBreakdown.html', args=args)

	
@app.route("/bookBreakdown")
def bookBreakdown():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset}

    #Title
    args["title"] = "Book Breakdown"
        
    #Get data, specify which publication type when calling the method
    args["data"] = db.getPublicationBreakDown("Book")
    args["description"] = "This page displays a breakdown of data for individual authors on book publications according to (a) number of sole author publications, (b) number of first author publications, (c) number of last author publications and (d) number of overall publications."

    return render_template('bookBreakdown.html', args=args)
	
	
@app.route("/bookChapterBreakdown")
def bookChapterBreakdown():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset}

    #Title
    args["title"] = "Book Chapter Breakdown"
        
    #Get data, specify which publication type when calling the method
    args["data"] = db.getPublicationBreakDown("Book Chapter")
    args["description"] = "This page displays a breakdown of data for individual authors on book chapter publications according to (a) number of sole author publications, (b) number of first author publications, (c) number of last author publications and (d) number of overall publications."

    return render_template('bookChapterBreakdown.html', args=args)
