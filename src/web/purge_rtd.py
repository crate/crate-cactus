import slumber
import requests
import argparse
import sys
import logging


login_url = 'https://readthedocs.org/accounts/login/'
wipe_url = 'https://readthedocs.org/wipe/{}/{}/'
build_url = 'https://readthedocs.org/build/{}'

projects = [
    "crash",
    "crate",
    "crate-dbal",
    "crate-java",
    "crate-jdbc",
    "crate-pdo",
    "crate-python"
]


logging.basicConfig()
logger = logging.getLogger('purge')
logger.setLevel(logging.DEBUG)


def rebuild_project(project_slug, session, api):
    offset = 0
    limit = 50
    while True:
        objects = api.version(project_slug).get(limit=limit, offset=offset)['objects']
        for obj in objects:
            project_id = obj['project']['id']
            if obj.get('built', False):
                logger.info("Wiping: {}".format(obj['slug']))
                res = session.post(wipe_url.format(project_slug, obj['slug']))
                status = res.status_code
                if status == 200:
                    logger.info("Building: {}...".format(obj['slug']))
                    res = session.post(build_url.format(project_id), data={"version_slug": obj['slug']})
                    status = res.status_code
                if status != 200:
                    logger.error("An error occured while rebuilding: \n {}".format(res))
        if len(objects) < limit:
            break
        offset += limit


def login(user, password):
    session = requests.Session()
    session.get(login_url)

    token = session.cookies.get('csrftoken')

    data = {"csrfmiddlewaretoken": token, "login": user, "password": password}
    session.post(login_url, data=data, headers={"referer": login_url})
    api = slumber.API(base_url='http://readthedocs.org/api/v1/', auth=(user, password))
    return session, api


def rebuild_all(user, password):
    session, api = login(user, password)
    for project in projects:
        logger.info("Purge: {}\n".format(project))
        rebuild_project(project, session, api)


def main(args=None, cb=sys.exit):
    parser = argparse.ArgumentParser(
        description="Rebuilds all crate read the docs projects")
    parser.add_argument('user')
    parser.add_argument('password')
    args = parser.parse_args()
    rebuild_all(args.user, args.password)


if __name__ == '__main__':
    main()
