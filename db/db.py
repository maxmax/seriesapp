#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi
from pymongo import MongoClient

# create a MongoDB client
client = MongoClient('localhost', 27017)

series_db = client['SeriesDB']
series_collection = series_db['series']


# > use SeriesDB
#> db.series.insertMany([
#... { _id: 1, name: "title1", year: 2012},
#... { _id: 2, name: "title2", year: 2013 },
#... { _id: 3, name: "title3", year: 2011}
#... ])

# > db.series.find({})

# > db.series.find({ year: 2013 })

# > db.series.updateOne({ name: "Suits" }, {
#     $set: { year: 2010 }
# })

#> db.series.deleteMany({ year: 2012 })
