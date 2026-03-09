$(warning $(shell tput bold setaf 1)Use just instead of make.$(shell tput sgr0))

# Forward all targets to just
.PHONY: _just_default_ $(MAKECMDGOALS)
_just_default_ $(MAKECMDGOALS) &::
	@just $(MAKECMDGOALS)
