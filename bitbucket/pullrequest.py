# -*- coding: utf-8 -*-
from .pullrequest_comment import PullRequestComment


URLS = {
    # Issues
    'GET_PULLREQUESTS': 'repositories/%(username)s/%(repo_slug)s/pullrequests/',
    'GET_PULLREQUEST': 'repositories/%(username)s/%(repo_slug)s/pullrequests/%(issue_id)s/',
    'CREATE_PULLREQUEST': 'repositories/%(username)s/%(repo_slug)s/pullrequests/',
    'UPDATE_PULLREQUEST': 'repositories/%(username)s/%(repo_slug)s/pullrequests/%(issue_id)s/',
    'APPROVE_PULLREQUEST': 'repositories/%(username)s/%(repo_slug)s/pullrequests/%(issue_id)s/approve',
    'DELETE_PULLREQUEST': 'repositories/%(username)s/%(repo_slug)s/pullrequests/%(issue_id)s/',
}


class PullRequest(object):
    """ This class provide issue-related methods to Bitbucket objects."""

    def __init__(self, bitbucket, pullrequest_id=None):
        self.bitbucket = bitbucket
        self.bitbucket.URLS.update(URLS)
        self.pullrequest_id = pullrequest_id
        self.comment = PullRequestComment(self)

    @property
    def pullrequest_id(self):
        """Your repository slug name."""
        return self._pullrequest_id

    @pullrequest_id.setter
    def pullrequest_id(self, value):
        if value:
            self._pullrequest_id = int(value)
        elif value is None:
            self._pullrequest_id = None

    @pullrequest_id.deleter
    def pullrequest_id(self):
        del self._pullrequest_id

    def all(self, repo_slug=None, params=None, owner=None):
        """ Get PullRequests from one of your repositories.
        """
        owner = owner or self.bitbucket.username
        repo_slug = repo_slug or self.bitbucket.repo_slug or ''
        url = self.bitbucket.url_v2('GET_PULLREQUESTS', username=owner, repo_slug=repo_slug)
        return self.bitbucket.dispatch_v2('GET', url, auth=self.bitbucket.auth, params=params)

    def get(self, pullrequest_id, repo_slug=None, owner=None):
        """ Get a PullRequest from one of your repositories.
        """
        repo_slug = repo_slug or self.bitbucket.repo_slug or ''
        owner = owner or self.bitbucket.username
        url = self.bitbucket.url_v2('GET_PULLREQUEST', username=owner, repo_slug=repo_slug, issue_id=pullrequest_id)
        return self.bitbucket.dispatch('GET', url, auth=self.bitbucket.auth)

    def create(self, repo_slug=None, owner=None, **kwargs):
        """
        Add a PullRequest to one of your repositories.
        Each issue require a different set of attributes,
        you can pass them as keyword arguments (attributename='attributevalue').
        Attributes are:

            * title: A string representing the request title.
            * description: The description of the pull request.
            * name:
            * milestone: The milestone associated with the issue.
            * version: The version associated with the issue.
            * responsible: The username of the person responsible for the issue.
            * status: The status of the issue (new, open, resolved, on hold, invalid, duplicate, or wontfix).
            * kind: The kind of issue (bug, enhancement, or proposal).
        """
        owner = owner or self.bitbucket.username
        repo_slug = repo_slug or self.bitbucket.repo_slug or ''
        url = self.bitbucket.url_v2('CREATE_PULLREQUEST', username=owner, repo_slug=repo_slug)
        return self.bitbucket.dispatch('POST', url, auth=self.bitbucket.auth, **kwargs)

    def approval(self, issue_id, http_func, repo_slug=None, owner=None, **kwargs):
        """
        Either add or remove approval from pull request
        """
        owner = owner or self.bitbucket.username
        repo_slug = repo_slug or self.bitbucket.repo_slug or ''
        url = self.bitbucket.url_v2('APPROVE_PULLREQUEST', username=owner,
                                    repo_slug=repo_slug, issue_id=issue_id)
        return self.bitbucket.dispatch(http_func, url,
                                       auth=self.bitbucket.auth,
                                       **kwargs)


    def approve(self, issue_id, repo_slug=None, owner=None, **kwargs):
        """
        Give your thumbs up on a pull request
        """
        return self.approval(issue_id, "POST", repo_slug, owner, **kwargs)

    def unapprove(self, issue_id, repo_slug=None, owner=None, **kwargs):
        """
        Remove your thumbs up from a pull request
        """
        return self.approval(issue_id, "DELETE", repo_slug, owner, **kwargs)

    def update(self, issue_id, repo_slug=None, owner=None, **kwargs):
        """
        Update an issue to one of your repositories.
        Each issue require a different set of attributes,
        you can pass them as keyword arguments (attributename='attributevalue').
        Attributes are:

            * title: The title of the new issue.
            * content: The content of the new issue.
            * component: The component associated with the issue.
            * milestone: The milestone associated with the issue.
            * version: The version associated with the issue.
            * responsible: The username of the person responsible for the issue.
            * status: The status of the issue (new, open, resolved, on hold, invalid, duplicate, or wontfix).
            * kind: The kind of issue (bug, enhancement, or proposal).
        """
        owner = owner or self.bitbucket.username
        repo_slug = repo_slug or self.bitbucket.repo_slug or ''
        url = self.bitbucket.url_v2('UPDATE_PULLREQUEST', username=owner, repo_slug=repo_slug, issue_id=issue_id)
        return self.bitbucket.dispatch('PUT', url, auth=self.bitbucket.auth, **kwargs)

    def delete(self, issue_id, repo_slug=None, owner=None):
        """ Delete an issue from one of your repositories.
        """
        owner = owner or self.bitbucket.username
        repo_slug = repo_slug or self.bitbucket.repo_slug or ''
        url = self.bitbucket.url_v2('DELETE_PULLREQUEST', username=owner, repo_slug=repo_slug, issue_id=issue_id)
        return self.bitbucket.dispatch('DELETE', url, auth=self.bitbucket.auth)
