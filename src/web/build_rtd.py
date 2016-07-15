import argparse
import sys
from web.purge_rtd import login, build_url, logger


def build(project_slug, version, user, password):
    session, api = login(user, password)
    obj = api.version(project_slug).get(limit=1)['objects'][0]
    project_id = obj['project']['id']
    res = session.post(build_url.format(project_id), data={"version_slug": version})
    status = res.status_code
    if status != 200:
        logger.error("An error occured while rebuilding: \n {}".format(res))


def main(args=None, cb=sys.exit):
    parser = argparse.ArgumentParser(
        description="Builds project on read the docs")
    parser.add_argument('project')
    parser.add_argument('--version', default="latest")
    parser.add_argument('user')
    parser.add_argument('password')
    args = parser.parse_args()
    build(args.project, args.version, args.user, args.password)


if __name__ == '__main__':
    main()
