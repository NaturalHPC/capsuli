Developing
==========

Making a release
----------------

There are four steps to making a release:

1. Choose the next version number

   It should be of the form ``x.y.z``, and be larger than all previous versions

2. Update the change log

   Edit ``CHANGELOG.md`` and add ``## x.y.z`` at the top with a description of the new
   version. Take care to keep the formatting and structure of the file intact, as the
   release automation relies on it.

3. Create a release PR

   Create a new pull request that merges ``develop`` into ``main`` and is titled
   ``Release x.y.z``. Wait for the checks to run, then check

   - that the release description is what you want (see the comment posted by the
     workflow),
   - that the documentation rendered correctly on ReadTheDocs (click the RTD check),
   - that there are no warnings in the package build (click on the "Build distribution"
     check)

   If there are any issues, put more commits onto ``develop`` to fix them; the PR will
   update accordingly as you go.

4. Merge the release PR

   Once happy, merge the PR, and check that the ``do_release`` workflow finished
   correctly. Congratulations, you have a release!

