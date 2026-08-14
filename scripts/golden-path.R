#!/usr/bin/env Rscript

## Build a throwaway package by running, verbatim, the scaffolding chain this repo tells users
## to run. Nothing here is a template: every file comes from biocthis. CI then puts the result
## through R CMD build, R CMD check and BiocCheck, so a green build means the instructions in
## AGENTS.md, SKILL.md and agents/bioc-package-review.md are instructions that were actually
## tested end to end, not instructions that merely look right.
##
## Usage:
##   Rscript scripts/golden-path.R [output-directory]
##
## Default output directory is /tmp/GoldenPathPkg (override with GOLDEN_PATH_DIR).
## scripts/verify.py asserts that every use_bioc_*() call in the documented block appears here.

options(
    usethis.quiet = TRUE,
    warn = 1,
    repos = c(CRAN = "https://cloud.r-project.org")
)

args <- commandArgs(trailingOnly = TRUE)
outdir <- if (length(args) >= 1) {
    args[[1]]
} else {
    Sys.getenv("GOLDEN_PATH_DIR", file.path(tempdir(), "GoldenPathPkg"))
}
pkg <- basename(outdir)

## use_bioc_vignette() calls usethis::use_package(), which check_installed()s each Suggests it
## adds - so BiocStyle and friends must be present, not merely declared. Finding that out here
## with a clear message beats finding it out mid-chain.
deps <- c(
    "usethis", "biocthis", "roxygen2",
    "BiocStyle", "knitr", "RefManageR", "sessioninfo", "testthat",
    "SummarizedExperiment"
)
for (dep in deps) {
    if (!requireNamespace(dep, quietly = TRUE)) {
        stop("golden-path needs ", dep, ": BiocManager::install(\"", dep, "\")", call. = FALSE)
    }
}

say <- function(...) cat("[golden-path]", ..., "\n", sep = " ")

if (dir.exists(outdir)) {
    say("removing previous", outdir)
    unlink(outdir, recursive = TRUE)
}
dir.create(dirname(outdir), recursive = TRUE, showWarnings = FALSE)

say("creating package", pkg, "in", outdir)
usethis::create_package(outdir, open = FALSE, rstudio = FALSE)
usethis::proj_set(outdir, force = TRUE)

## A package with no code has nothing to document, and BiocCheck has opinions about that. One
## exported function, written in Bioconductor style (assignment arrow, four-space indent,
## seq_along rather than 1:n) so the example is not quietly teaching the wrong habits.
dir.create(file.path(outdir, "R"), showWarnings = FALSE)
writeLines(
    c(
        "#' Count observed values per sample",
        "#'",
        "#' @param se A [SummarizedExperiment::SummarizedExperiment].",
        "#' @param assay_name Name or index of the assay to count.",
        "#'",
        "#' @return An integer vector with one element per column of `se`.",
        "#'",
        "#' @examples",
        "#' library(SummarizedExperiment)",
        "#' counts <- matrix(c(1, NA, 3, 4), nrow = 2)",
        "#' se <- SummarizedExperiment(assays = list(counts = counts))",
        "#' countObserved(se)",
        "#'",
        "#' @importFrom SummarizedExperiment assay",
        "#' @export",
        "countObserved <- function(se, assay_name = 1L) {",
        "    mat <- SummarizedExperiment::assay(se, assay_name)",
        "    counts <- integer(ncol(mat))",
        "    for (i in seq_along(counts)) {",
        "        counts[[i]] <- sum(!is.na(mat[, i]))",
        "    }",
        "    names(counts) <- colnames(mat)",
        "    counts",
        "}"
    ),
    file.path(outdir, "R", "countObserved.R")
)

## Unit tests, because the guide asks for them and BiocCheck says so out loud ("Consider adding
## unit tests. We strongly encourage them."). A fixture that skips them is not modelling the
## package we tell people to submit.
dir.create(file.path(outdir, "tests", "testthat"), recursive = TRUE, showWarnings = FALSE)
writeLines(
    c(
        'library(testthat)',
        paste0('library(', pkg, ')'),
        '',
        paste0('test_check("', pkg, '")')
    ),
    file.path(outdir, "tests", "testthat.R")
)
writeLines(
    c(
        'test_that("countObserved counts non-missing values per sample", {',
        '    counts <- matrix(c(1, NA, 3, 4), nrow = 2)',
        '    se <- SummarizedExperiment::SummarizedExperiment(',
        '        assays = list(counts = counts)',
        '    )',
        '    expect_identical(countObserved(se), c(1L, 2L))',
        '})',
        '',
        'test_that("countObserved rejects a non-SummarizedExperiment", {',
        '    expect_error(countObserved(1:3))',
        '})'
    ),
    file.path(outdir, "tests", "testthat", "test-countObserved.R")
)

## ---------------------------------------------------------------------------------------
## The documented chain. Keep these calls identical to the block in AGENTS.md, SKILL.md and
## agents/bioc-package-review.md - verify.py check 8 fails the build if they drift apart.
## ---------------------------------------------------------------------------------------

## use_bioc_description() goes through usethis::write_over(), which will not replace an existing
## file without approval and declines silently when it cannot ask. create_package() has just
## written a DESCRIPTION, so leaving it in place would make the next call a silent no-op and the
## package would end up with no biocViews. Removing it is what "approve the overwrite" amounts
## to. On a real existing package the honest advice is the opposite: add biocViews by hand rather
## than let this discard your metadata.
unlink(desc_path <- file.path(outdir, "DESCRIPTION"))

say("biocthis::use_bioc_description()")
biocthis::use_bioc_description(biocViews = "Software, GeneExpression, Transcriptomics")

say("biocthis::use_bioc_news_md()")
biocthis::use_bioc_news_md(open = FALSE)

say("biocthis::use_bioc_vignette()")
biocthis::use_bioc_vignette(name = pkg, title = paste("Introduction to", pkg))

say("biocthis::use_bioc_citation()")
biocthis::use_bioc_citation()

say("biocthis::use_bioc_github_action()")
biocthis::use_bioc_github_action()

## ---------------------------------------------------------------------------------------
## The two things the guide requires that biocthis does not decide for you.
## ---------------------------------------------------------------------------------------

## BiocCheck warns that a scaffolded Description is "too concise" and that a Software package
## with no Bioconductor dependencies should consider CRAN. Both are real submission feedback, so
## the fixture answers them rather than suppressing them: a Description of several sentences, and
## a genuine SummarizedExperiment dependency - which is also the reuse rule this repo teaches.
say("writing a Description of substance and declaring the Bioconductor dependency")
desc <- readLines(desc_path)
desc <- desc[!grepl("^(Title|Description|Imports):", desc)]
desc <- c(
    desc,
    paste(
        "Title: Count Observed Values Per Sample In A SummarizedExperiment"
    ),
    paste(
        "Description: Counts the non-missing values in each column of an assay stored in a",
        "SummarizedExperiment object. The result is one integer per sample, which is a common",
        "first step when assessing coverage or sparsity across an experiment. This package",
        "exists to exercise the scaffolding chain documented in AGENTS.md and is not intended",
        "for analysis."
    ),
    "Imports: SummarizedExperiment"
)
writeLines(desc, desc_path)

say("confirming Version: 0.99.0")
desc <- readLines(desc_path)
desc[grepl("^Version:", desc)] <- "Version: 0.99.0"
writeLines(desc, desc_path)

## biocthis 1.23.0 ships inst/CITATION with an empty title: the template substitutes {{Title}}
## but use_bioc_citation() never passes one. citation() errors on an empty title, the generated
## vignette calls citation(), and so R CMD build fails at "creating vignettes". A real user has
## to fill this file in anyway - the DOI in it is the literal string 10.1101/TODO - so doing the
## minimum here is modelling the user, not papering over the bug.
say("filling in the CITATION fields that use_bioc_citation() leaves empty")
cit_path <- file.path(outdir, "inst", "CITATION")
cit <- readLines(cit_path)
holes <- c('title = ""', 'as.person("")')
if (!any(vapply(holes, function(h) any(grepl(h, cit, fixed = TRUE)), logical(1)))) {
    warning(
        "inst/CITATION has no empty title or author - biocthis may have fixed this. ",
        "Re-check before keeping this workaround.",
        call. = FALSE
    )
}
cit <- sub('title = ""', paste0('title = "', pkg, ': a golden-path fixture"'), cit, fixed = TRUE)
cit <- sub('as.person("")', 'as.person("Golden Path")', cit, fixed = TRUE)
writeLines(cit, cit_path)

say("roxygenise (man pages for exported objects)")
roxygen2::roxygenise(outdir, load_code = roxygen2::load_source)

## ---------------------------------------------------------------------------------------
## Assert the chain produced what the gate asks for. A silent rename upstream (a use_bioc_*()
## function that no longer writes NEWS.md, say) has to fail here rather than three steps later
## inside BiocCheck output nobody reads.
## ---------------------------------------------------------------------------------------

expected <- c(
    "DESCRIPTION",
    "NAMESPACE",
    "NEWS.md",
    "inst/CITATION",
    file.path("vignettes", paste0(pkg, ".Rmd")),
    file.path("man", "countObserved.Rd"),
    file.path("tests", "testthat.R")
)
missing <- expected[!file.exists(file.path(outdir, expected))]
if (length(missing) > 0L) {
    stop(
        "the documented scaffolding chain did not produce: ",
        paste(missing, collapse = ", "),
        call. = FALSE
    )
}

desc <- readLines(desc_path)
if (!any(grepl("^Version: 0\\.99\\.0$", desc))) {
    stop("DESCRIPTION is not at Version: 0.99.0", call. = FALSE)
}
if (!any(grepl("^biocViews:", desc))) {
    stop("use_bioc_description() no longer writes a biocViews field", call. = FALSE)
}

say("ok:", outdir)
cat(outdir, "\n", sep = "")
