
URLS = {
    # Issues
    'GET_COMMITS': 'repositories/%(team)s/%(repo_slug)s/commits',
    'GET_COMMIT': 'repositories/%(team)s/%(repo_slug)s/commit/%(gitsha)s',
    'GET_BUILDS': 'repositories/%(team)s/%(repo_slug)s/commit/%(gitsha)s/statuses',
    'GET_BUILD': 'repositories/%(team)s/%(repo_slug)s/commit/%(gitsha)s/statuses/build/%(key)s',
    'POST_BUILD': 'repositories/%(team)s/%(repo_slug)s/commit/%(gitsha)s/statuses/build',
}


class Commit(object):

    def __init__(self, bitbucket, team, gitsha, repo_slug=None, owner=None):
        """
        :param bitbucket: A bitbucket object
        :type bitbucket: `bitbucket.Bitbucket`
        :param repository: The Bitbucket repo
        :type repository: `str`
        :param gitsha: The sha of the commit this build was applied to
        :type gitsha: `str`
        :param repo_slug: The repository name. If not supplied uses the one from the bitbucket \
            object
        :type repo_slug: `str`
        :param owner: The bitbucket team. If not supplied uses the one from the bitbucket object.
        :type owner: `str`
        """
        self.bitbucket = bitbucket
        self.bitbucket.URLS.update(URLS)
        self.gitsha = gitsha
        self.repo_slug = repo_slug or self.bitbucket.repo_slug
        self.team = team
        self.username = owner or self.bitbucket.username
        if repo_slug is None:
            self.repo_slug = repo_slug
        url = self.bitbucket.url_apiv2('GET_COMMIT', team=self.team, repo_slug=self.repo_slug,
                                       gitsha=self.gitsha)
        (success, result) = self.bitbucket.dispatch(
            'GET', url, auth=self.bitbucket.auth)
        if success:
            for key in result:
                if not hasattr(self, key):
                    setattr(self, key, result[key])

    @property
    def builds(self):
        """
        :returns: All the builds for this commit
        :rtype: `list` of `bitbucket.Build`
        """
        url = self.bitbucket.url_apiv2('GET_BUILDS', team=self.team, repo_slug=self.repo_slug,
                                       gitsha=self.gitsha)
        (success, result) = self.bitbucket.dispatch(
            'GET', url, auth=self.bitbucket.auth)
        if success:
            retval = []
            for build in result['values']:
                retval.append(Build(commit=self, **build))
            return retval
        else:
            raise Exception(result)

    def get_build(self, key):
        """
        :param key: The key of the build for this commit
        :type key: `str`
        :returns: A Build object. Raises Exception if it doesn't exist.
        :rtype: `bitbucket.Build`
        """
        url = self.bitbucket.url_apiv2('GET_BUILD', team=self.team, repo_slug=self.repo_slug,
                                       gitsha=self.gitsha, key=key)
        (success, result) = self.bitbucket.dispatch(
            'GET', url, auth=self.bitbucket.auth)
        if success:
            return Build(commit=self, **result)
        else:
            raise Exception(result)

    def register_build(self, state, key, url, name=None, description=None):
        """
        :param state: The state of the build.
        :type state: `bitbucket.BuildState`
        :param key: The key of the build for this commit
        :type key: `str`
        :param url: The url to find more information about the build
        :type url: `str`
        :param name: An OPTIONAL name for the build
        :type name: `str`
        :param description: An OPTIONAL description for the build
        :returns: The new Build object
        :rtype: `bitbucket.Build`
        """
        if not hasattr(BuildState, state):
            raise AttributeError("state must be a BuildState attribute")
        bb_url = self.bitbucket.url_apiv2('POST_BUILD', team=self.team, repo_slug=self.repo_slug,
                                       gitsha=self.gitsha)
        for build in self.builds:
            # If another build of the same name is found then update it.
            if build.key == key:
                build.update(state=state, url=url, name=name, description=description)
                return self.get_build(key)
        data = {"state": state,
                "key": key,
                "url": url}
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        (success, result) = self.bitbucket.dispatch_v2("POST", bb_url, auth=self.bitbucket.auth,
                                                    data=data)
        if success:
            return self.get_build(key)
        else:
            raise Exception(result)


class Build(object):

    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def update(self, state=None, name=None, url=None, description=None):
        """
        Update information about the build
        :param state: The state of the build.
        :type state: `bitbucket.BuildState`
        :param name: An OPTIONAL name for the build
        :type name: `str`
        :param url: The url to find more information about the build
        :type url: `str`
        :param description: An OPTIONAL description for the build
        """
        if not state is None and not hasattr(BuildState, state):
            raise AttributeError("state must be a BuildState attribute")
        bb_url = self.commit.bitbucket.url_apiv2('GET_BUILD', team=self.commit.team, 
                                          repo_slug=self.commit.repo_slug,
                                          gitsha=self.commit.gitsha, key=self.key)
        data = {}
        if state:
            data['state'] = state
        if name:
            data['name'] = name
        if url:
            data['url'] = url
        if description:
            data['description'] = description
        if len(data.keys()) > 0:
            self.commit.bitbucket.dispatch_v2("PUT", bb_url, auth=self.commit.bitbucket.auth,
                                              data=data)
            for key in data.keys():
                setattr(self, key, data[key])


class BuildState(object):
    """
    Acceptable build states for bitbucket
    Can't deviate from these- probably an enum
    """
    SUCCESSFUL = "SUCCESSFUL"
    INPROGRESS = "INPROGRESS"
    FAILED = "FAILED"
    STOPPED = "STOPPED"
