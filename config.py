newrelic_user_key = ''
newrelic_account_id = ''
azure_connection_string = ''
azure_container = ''
queries = [
    {
        'name':'Apdex & Page Count per Client',
        'query':"FROM PageView SELECT count(*), apdex(duration, t: 4) AS 'Apdex t:4', apdex(duration, t: 7) AS 'Apdex t:7' FACET appName SINCE 30 days ago LIMIT MAX"
    },
    {
        'name':'Ultra clients Apdex & Page count',
        'query':"From PageView WITH position(pageUrl, '/', 2) AS startpage, substring(pageUrl, startpage) AS page SELECT count(*), apdex(duration, t: 4) as 'Apdex t:4', apdex(duration, t: 7) as 'Apdex t:7' WHERE pageUrl LIKE '%ultra%' FACET appName since 30 days ago LIMIT MAX"
    },
    {
        'name':'Apdex & Page Count per Client(Onlyt4)',
        'query':"FROM PageView SELECT count(*), apdex(duration, t: 4) AS 'Apdex t:4' FACET appName SINCE 30 days ago LIMIT MAX"
    },
    {
        'name':'Ultra clients Apdex & Page count (Onlyt4)',
        'query':"From PageView WITH position(pageUrl, '/', 2) AS startpage, substring(pageUrl, startpage) AS page SELECT count(*), apdex(duration, t: 4) as 'Apdex t:4' WHERE pageUrl LIKE '%ultra%' FACET appName since 30 days ago LIMIT MAX"
    },
    {
        'name':'Percentile 95 Per Page',
        'query':"FROM PageView SELECT count(*), percentile(duration, 95), apdex(duration, t: 4) AS 'Apdex t:4' FACET name SINCE 30 days ago LIMIT MAX"
    },
    {
        'name':'Apdex Per Client(Onlyt4)',
        'query':"FROM PageView SELECT count(*), apdex(duration, t: 4) AS 'Apdex t:4' FACET appName SINCE 30 days ago LIMIT MAX"
    },
    {
        'name':'Apdex Per URL Ultra',
        'query':"From PageView WITH position(pageUrl, '/', 2) AS startpage, substring(pageUrl, startpage) AS page SELECT apdex(duration, t: 4) as 'Apdex t:4', apdex(duration, t: 7) as 'Apdex t:7' WHERE pageUrl LIKE '%ultra%' FACET page since 30 days ago LIMIT MAX"
    },
    {
        'name':'Apdex Per Transaction Name Ultra',
        'query':"From PageView SELECT apdex(duration, t: 4) as 'Apdex t:4', apdex(duration, t: 7) as 'Apdex t:7' WHERE pageUrl LIKE '%ultra%' FACET name since 30 days ago LIMIT MAX"
    },
    {
        'name':'Apdex All Clients',
        'query':"FROM PageView SELECT apdex(duration, t: 4) AS 'Apdex t:4', apdex(duration, t: 7) AS 'Apdex t:7' SINCE 30 days ago LIMIT MAX"
    }
]
