class Mlface < Formula
  desc "ML Face Recognition Service"
  homepage "https://github.com/ccoupe/mlface"
  url "file:///usr/local/lib/mlface"
  version "1.1.0"

  def install
    # The files are already in /usr/local/lib/mlface via the Makefile
    # We just need brew to manage the service pointing to the right place
    (bin/"mlface-service").write <<~EOS
      #!/bin/bash
      exec /usr/local/lib/mlface/launch_mlface.sh
    EOS
  end

  service do
    run [opt_bin/"mlface-service"]
    working_dir "/usr/local/lib/mlface"
    keep_alive true
    log_path "/usr/local/var/log/mlface.log"
    error_log_path "/usr/local/var/log/mlface.log"
  end
end
