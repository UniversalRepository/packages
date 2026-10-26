<!--
Use the commit/title style described in CONTRIBUTING.md.
For example: void/foo: update to 1.2.3

Delete sections and checklist items which do not apply.
You can open a draft PR even if the work is unfinished.
Leave unfinished items unchecked and explain where help is needed.
-->

## Description

<!--
Briefly explain what this changes and why.
For a new package, explain what it does and link upstream.
If copied from elsewhere, include the original source.

For a simple version update, this section can be removed.
Link any related issues, e.g. Closes #123.
-->

## Testing

<!--
Mention the distro, architecture/libc, commands used, and results.
For packages, please also test installing and running them where applicable.
Include relevant logs or workflow runs.

If you couldn't test something, mention it here.
-->

## Checklist

- [ ] I have read [CONTRIBUTING.md](https://github.com/UniversalRepository/packages/blob/master/CONTRIBUTING.md)
- [ ] The commits follow the documented commit style

### Package changes

- [ ] The template follows the respective distro's packaging guidelines
- [ ] Applicable lint checks pass
- [ ] I built the package locally for my architecture
- [ ] I tested installing and running it, or explained why I couldn't
- [ ] Version, revision/release, checksums, and dependencies are updated where needed
- [ ] Known architecture/libc restrictions are included

<!-- For new packages only -->

- [ ] The license allows us to redistribute the package
- [ ] I intend to maintain this package, or mentioned where help is needed

### Backend or build system changes

- [ ] I explained what changed and why
- [ ] I tested the affected backends
- [ ] Local builds do not require CI or publishing credentials

<!--
For a new backend, or changes affecting the following behavior,
keep the relevant items.
-->

- [ ] Multiple targets and subpackages work where supported
- [ ] Package selection notices missing packages/subpackages and changed versions/revisions
- [ ] Adding a package keeps existing packages in the repository metadata
- [ ] Installing from the generated repository works with signature verification
- [ ] Necessary container, CI, signing, and package index changes are included
- [ ] Failed builds return a nonzero status and do not publish incomplete results
- [ ] Documentation is updated, including any remaining limitations
