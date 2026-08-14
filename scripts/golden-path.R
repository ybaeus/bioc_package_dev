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
    "BiocStyle", "knitr", "RefManageR", "sessioninfo", "testthat"
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
        "#' Count non-missing values per column",
        "#'",
        "#' @param x A `data.frame` or matrix.",
        "#'",
        "#' @return An integer vector, one element per column of `x`.",
        "#'",
        "#' @examples",
        "#' countObserved(data.frame(a = c(1, NA), b = c(2, 3)))",
        "#'",
        "#' @export",
        "countObserved <- function(x) {",
        "    stopifnot(length(dim(x)) == 2L)",
        "    counts <- integer(ncol(x))",
        "    for (i in seq_along(counts)) {",
        "        counts[[i]] <- sum(!is.na(x[, i]))",
        "    }",
        "    names(counts) <- colnames(x)",
        "    counts",
        "}"
    ),
    file.path(outdir, "R", "countObserved.R")
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
biocthis::use_bioc_description(biocViews = "Software")

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

say("confirming Version: 0.99.0")
desc <- readLines(desc_path)
desc[grepl("^Version:", desc)] <- "Version: 0.99.0"
writeLines(desc, desc_path)

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
    file.path("man", "countObserved.Rd")
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
