# How to Contribute to aiochannel

## Bugs

### Discovering a bug

Before you open a new issue,
**ensure that the bug was not already reported** by searching all issues
(also closed ones) for a duplicate of your bug.
If nobody else has reported the bug, open a new issue.

The issue must contain - at the very minimum - a summary of the problem and
a small-as-possible way to reproduce the bug.

### Fixing a bug

If you wrote a patch to fix a bug, open a Pull Request with the patch.

Your PR must contain:

1. Test cases that exposes the bug (they will fail without your patch)
2. The patch that fixes your test case.
3. Test cases that ensures code-coverage of your patch.
4. A description of what the PR fixes. Ideally with a reference to the issue
   in the bug tracker with the problem, or a PR description that is equivalent.

## Maintenance & Upgrades

If you want to support a new version of python, extend / improve the tests,
or in other ways improve the development of the library, open up a PR with
your changes.

## Features

**Please** note that it is unlikely that any new features will
be added to the library, and most PRs intended to extend the functionality
of `aiochannel` without thorough rationale for doing so, **will be rejected**.
This might seem surprising, but is core to the philosophy of library development for the author.
If you still think your feature is worth adding:

If you want to suggest a feature, open a new issue with the suggestion,
after checking that it has not been suggested before.

You are expected to implement your own feature request,
so once the new feature has been discussed, you must open a PR adding the new feature.
