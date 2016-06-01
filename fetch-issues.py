#!/usr/bin/env python3


from collections import namedtuple
import os.path
import csv
import io
import json
import requests
import time

USER_HOME = os.path.expanduser("~")
SECRETS_FILE = os.path.join(USER_HOME, "fetch-issues.json")


def get_secret(key):
    with open(SECRETS_FILE) as f:
        return json.load(f)[key]


Issue = namedtuple("Issue", ["created", "title", "url"])


def github_parser(json_string, ticket_base_url):
    return (
        Issue(
            created=issue["created_at"].split("T")[0],
            title=issue["title"],
            url="/".join([ticket_base_url, str(issue["number"])]),
        )
        for issue in json.loads(json_string)
    )


def redmine_parser(json_string, ticket_base_url):
    return (
        Issue(
            created=issue["start_date"],
            title=issue["subject"],
            url="/".join([ticket_base_url, str(issue["id"])]),
        )
        for issue in json.loads(json_string)["issues"]
    )


def trac_parser(csv_string, ticket_base_url):
    return (
        Issue(
            created=issue["time"].split(" ")[0],
            title=issue["summary"],
            url="/".join([ticket_base_url, issue["\ufeffid"]]),
        )
        for issue in csv.DictReader(io.StringIO(csv_string))
    )


def mantis_parser(csv_string, ticket_base_url):
    return (
        Issue(
            created=issue["Date Submitted"],
            title=issue["Summary"],
            url="{}{}".format(ticket_base_url, issue["Id"]),
        )
        for issue in csv.DictReader(io.StringIO(csv_string))
    )


IssueTracker = namedtuple(
    "IssueTracker",
    ["parser", "project", "url", "headers", "ticket_base_url"],
)


issue_trackers = [
    IssueTracker(
        parser=trac_parser,
        project="OpenModelica",
        url="https://trac.openmodelica.org/OpenModelica/query?status=accepted&status=assigned&status=new&status=reopened&summary=~into-cps&or&status=accepted&status=assigned&status=new&status=reopened&description=~into-cps&format=csv&col=id&col=summary&col=time&order=priority",  # noqa
        headers=None,
        ticket_base_url="https://trac.openmodelica.org/OpenModelica/ticket",
    ),
    IssueTracker(
        parser=redmine_parser,
        project="Modelio",
        url="http://forge.modelio.org/projects/intocps/issues.json",
        headers=None,
        ticket_base_url="http://forge.modelio.org/issues",
    ),
    IssueTracker(
        parser=github_parser,
        project="INTO-CPS Application",
        url="https://api.github.com/repos/into-cps/INTO-CPS_Application/issues?state=open",  # noqa
        headers=None,
        ticket_base_url="https://github.com/into-cps/INTO-CPS_Application/issues",  # noqa
    ),
    IssueTracker(
        parser=github_parser,
        project="Overture",
        url="https://api.github.com/repos/overturetool/overture/issues?state=open&labels=into-cps",  # noqa
        headers=None,
        ticket_base_url="https://github.com/overturetool/overture/issues",
    ),
    IssueTracker(
        parser=github_parser,
        project="Overture-FMU",
        url="https://api.github.com/repos/overturetool/overture-fmu/issues?state=open",  # noqa
        headers=None,
        ticket_base_url="https://github.com/overturetool/overture-fmu/issues",  # noqa
    ),
    IssueTracker(
        parser=github_parser,
        project="20-sim FMU Export",
        url="https://api.github.com/repos/controllab/fmi-export-20sim/issues?state=open",  # noqa
        headers=None,
        ticket_base_url="https://github.com/controllab/fmi-export-20sim/issues",  # noqa
    ),

    IssueTracker(
        parser=github_parser,
        project="INTO-CPS DSE",
        url="https://api.github.com/repos/CarlGamble/INTO-CPS-DSE/issues?state=open",  # noqa
        headers=None,
        ticket_base_url="https://github.com/CarlGamble/INTO-CPS-DSE/issues",
    ),
    IssueTracker(
        parser=github_parser,
        project="INTO-CPS UI",
        url="https://api.github.com/repos/into-cps/intocps-ui/issues?state=open",  # noqa
        headers=None,
        ticket_base_url="https://github.com/into-cps/intocps-ui/issues",
    ),
#    IssueTracker(
#        parser=mantis_parser,
#        project="RT-Tester",
#        url="https://software.verified.de/mantis/csv_export.php",
#        headers=get_secret("rtt_headers"),
#        ticket_base_url="https://software.verified.de/mantis/view.php?id=",
#    ),
]


def main():
    
    timestr = time.strftime("%Y-W%W")#"%Y-%m-%d")
    print (timestr)
    week = time.strftime("%W")
    year = time.strftime("%Y")
    name = '{}-W{}'.format(year,week)
    fileName = name+'.md'
    
    fc = open('fetch-out','w')
    fc.write(fileName)
    fc.close()
    
    f = open(fileName,'w')
    f.write('---\n')
    f.write('layout: default\n')
    f.write('title: Week {} {}, Weekly Issues Digest\n'.format(week,year))
    f.write('---\n\n')

    f.write('# Week {} {}, Weekly Issues Digest for INTO-CPS\n\n'.format(week,year))

    f.write('## Currently Open Issues\n\n')
    
    for tracker in sorted(issue_trackers, key=lambda tracker: tracker.project):
        print("### {}".format(tracker.project))
        for issue in tracker.parser(
            requests.get(tracker.url, headers=tracker.headers).text,
            tracker.ticket_base_url,
        ):
            line = "* [{} - ({})]({})".format(
                    issue.title,
                    issue.created,
                    issue.url,
                )
            f.write(line+'\n')
            print(line)
    f.write("\n\n#History of Weekly Digests\n\n")
    f.write("Below you will find a list of weekly digests giving a historical overview of all known issues across all the tools that are part of INTO-CPS.\n")
    

    with open('issue-history.txt','rw') as fc:
        my_lines = fc.readlines()
        fc.close()

        for s in my_lines:
            f.write("* [{}]({}.html)".format(s,s))

        
        if any(name in s for s in my_lines):
            print("already there\n")
        else:
            lines = [name]+ my_lines
       
            with open('issue-history.txt','w') as fh:
                fh.writelines(["%s\n" % item  for item in lines])
                fh.close()
        
    f.close()
                
if __name__ == "__main__":
    main()
