variable "ledger_path" {
  type        = string
  description = "Path to the corrupted CSV ledger"
}

variable "output_dir" {
  type        = string
  description = "Path to the directory to write output artifacts"
}

resource "terraform_data" "recovery" {
  input = var.ledger_path

  provisioner "local-exec" {
    command = "python3 ${path.module}/recover.py --ledger ${var.ledger_path} --output-dir ${var.output_dir}"
  }
}
