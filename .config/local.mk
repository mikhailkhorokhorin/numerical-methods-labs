REPORT_LABS := $(sort $(patsubst %/report/report.tex,%,$(wildcard lab*/report/report.tex)))
REPORT_BUILD_DIR := $(CURDIR)/build/report
REPORT_ARTIFACTS_DIR := $(CURDIR)/build/artifacts/reports
LATEXMK := latexmk -pdf -interaction=nonstopmode -halt-on-error

CI_EXTRA := reports

.PHONY: reports report

reports: $(addprefix report-,$(REPORT_LABS))

report:
	@test -n "$(LAB)" || (echo "LAB is required" >&2; exit 2)
	$(MAKE) report-$(LAB)

report-%:
	mkdir -p $(REPORT_BUILD_DIR)/$* $(REPORT_ARTIFACTS_DIR)
	cd $*/report && epoch=$$(git log -1 --format=%ct -- . 2>/dev/null) && \
		SOURCE_DATE_EPOCH=$${epoch:-$$(date +%s)} FORCE_SOURCE_DATE=1 \
		$(LATEXMK) -outdir=$(REPORT_BUILD_DIR)/$* report.tex
	cp $(REPORT_BUILD_DIR)/$*/report.pdf $*/report/report.pdf
	cp $(REPORT_BUILD_DIR)/$*/report.pdf $(REPORT_ARTIFACTS_DIR)/$*.pdf
