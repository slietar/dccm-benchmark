library(bio3d)

source("./tools.r")


dirs <- commandArgs(trailingOnly=TRUE)

ligand_mass <- list(153.18 / 11, 654.6 / 43)
names(ligand_mass) <- c("DPA", "BRC")


output <- c()

for (dir_index in 1:length(dirs)) {
  dir = dirs[dir_index]
  file_list = read.table(file.path(dir, "file_list.txt"))
  ligand_path = file.path(dir, "ligand.pdb")

  if (file.exists(ligand_path)) {
    ligand_data = read.pdb(ligand_path)
  } else {
    ligand_data <- NULL
  }

  dc_list0 <- c()

  write(sprintf("* %s", dir), stderr())

  for (file in file_list[[1]]) {
    write(sprintf("  * %s", file), stderr())
    input_data <- read.pdb(file.path(dir, trimws(file)))

    if (!is.null(ligand_data)) {
      data <- cat.pdb(input_data, ligand_data, rechain=TRUE, renumber=FALSE)
    } else {
      data <- input_data
    }

    capture.output(inds <- combine.select(
      atom.select(data, type="ATOM", elety="CA", operator="AND"),
      atom.select(data, type="HETATM", string="noh", operator="AND"),
      operator="OR"
    ), file="/dev/null")

    capture.output(dccm_pdb_data0 <- dccm(supernma(data), nmodes=20, ncore=1), file="/dev/null")
    capture.output(dccm_pdb_data1 <- dccm(supernma(data, inds, mass.custom=ligand_mass), nmodes=20, ncore=1), file="/dev/null")


    a0 <- matrix(0, nrow=540, ncol=540)
    a0[1:ncol(dccm_pdb_data0), 1:ncol(dccm_pdb_data0)] <- dccm_pdb_data0

    a1 <- matrix(0, nrow=540, ncol=540)
    a1[1:ncol(dccm_pdb_data1), 1:ncol(dccm_pdb_data1)] <- dccm_pdb_data1

    dc_list0 <- c(dc_list0, c(a0), c(a1))
  }

  output <- c(output, dc_list0)
}

capture.output(warnings(), file=stderr())


write("* Saving...", stderr())

outpath <- tempfile()
saveRDS(data.frame(output), outpath)

con <- pipe("cat", "wb")
writeBin(readBin(outpath, raw(), file.info(outpath)$size), con)
flush(con)
