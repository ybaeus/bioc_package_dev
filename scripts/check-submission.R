#!/usr/bin/env Rscript

# check-submission.R
# Run the Bioconductor pre-submission gate against a package and report pass/fail.
# Usage:
#   Rscript check-submission.R [path/to/package]
# Defaults to the current directory. Requires R-devel plus the BiocCheck package.
# This is a convenience wrapper; the authoritative checks are R CMD check and BiocCheck.

args <- commandArgs(trailingOnly = TRUE)
pkg_dir <- if (length(args) >= 1) args[[1]] else "."
pkg_dir <- normalizePath(pkg_dir, mustWork = TRUE)

desc_path <- file.path(pkg_dir, "DESCRIPTION")
if (!file.exists(desc_path)) {
    stop("No DESCRIPTION found in '", pkg_dir, "'. Point this at a package root.")
}

pass <- character(0)
fail <- character(0)
note <- character(0)
record <- function(ok, msg) {
    if (isTRUE(ok)) pass[[length(pass) + 1]] <<- msg
    else fail[[length(fail) + 1]] <<- msg
}

dcf <- read.dcf(desc_path)
field <- function(name) if (name %in% colnames(dcf)) trimws(dcf[1, name]) else NA_character_

# --- Static gate checks (no build required) ---
version <- field("Version")
record(!is.na(version) && grepl("^0\\.99\\.[0-9]+$", version),
       sprintf("Version is 0.99.z for a new package (found: %s)", version))

record(!is.na(field("biocViews")) && nzchar(field("biocViews")),
       "biocViews field present")

maint <- field("Authors@R")
if (is.na(maint) || !nzchar(maint)) maint <- field("Maintainer")
record(!is.na(maint) && grepl("[[:alnum:]._%+-]+@[[:alnum:].-]+", maint),
       "Maintainer with an email present")

record(dir.exists(file.path(pkg_dir, "vignettes")),
       "vignettes/ directory present")

record(dir.exists(file.path(pkg_dir, "man")),
       "man/ directory present")

record(dir.exists(file.path(pkg_dir, "tests")),
       "tests/ directory present")

# Individual file size <= 5 MB
all_files <- list.files(pkg_dir, recursive = TRUE, full.names = TRUE, all.files = TRUE, no.. = TRUE)
big <- all_files[file.size(all_files) > 5 * 1024^2]
big <- big[!grepl("(^|/)\\.git/", big)]
record(length(big) == 0,
       if (length(big) == 0) "No individual file exceeds 5 MB"
       else sprintf("Files exceed 5 MB: %s", paste(basename(big), collapse = ", ")))

# --- Dynamic checks (BiocCheck), if available ---
if (requireNamespace("BiocCheck", quietly = TRUE)) {
    message("Running BiocCheck::BiocCheck('new-package' = TRUE) ...")
    res <- tryCatch(
        BiocCheck::BiocCheck(pkg_dir, `new-package` = TRUE),
        error = function(e) { message("BiocCheck errored: ", conditionMessage(e)); NULL }
    )
    if (!is.null(res)) {
        n_err <- tryCatch(length(res$error), error = function(e) NA_integer_)
        n_warn <- tryCatch(length(res$warning), error = function(e) NA_integer_)
        record(isTRUE(n_err == 0),
               sprintf("BiocCheck errors: %s", ifelse(is.na(n_err), "unknown", n_err)))
        record(isTRUE(n_warn == 0),
               sprintf("BiocCheck warnings: %s", ifelse(is.na(n_warn), "unknown", n_warn)))
    }
} else {
    note[[length(note) + 1]] <- paste(
        "BiocCheck not installed - skipped R CMD check / BiocCheck. Install with",
        "BiocManager::install('BiocCheck'), then run R CMD check and BiocCheck manually.")
}

# --- Report ---
cat("\n=== Bioconductor pre-submission gate ===\n")
cat("Package:", field("Package"), "at", pkg_dir, "\n\n")
if (length(pass)) cat("PASS:\n", paste0("  - ", pass, collapse = "\n"), "\n", sep = "")
if (length(fail)) cat("\nFAIL:\n", paste0("  - ", fail, collapse = "\n"), "\n", sep = "")
if (length(note)) cat("\nNOTES:\n", paste0("  - ", note, collapse = "\n"), "\n", sep = "")

cat("\nReminder: this wrapper does not replace `R CMD check` on R-devel. Run it, plus\n")
cat("BiocCheck::BiocCheckGitClone(), before opening a submission issue.\n")

quit(status = if (length(fail) > 0) 1L else 0L)
