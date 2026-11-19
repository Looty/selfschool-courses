# The broken box: a Debian machine with seven classic faults.
# Build:  docker build -t pce-ch05-broken-box .
# Run:    see lesson 4 of chapter 5 (the spool needs a small tmpfs with an inode limit).
FROM debian:bookworm-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      procps psmisc iproute2 lsof strace python3 less nano vim-tiny \
 && rm -rf /var/lib/apt/lists/*

# Service accounts.
RUN useradd --system --no-create-home --shell /usr/sbin/nologin vmapi \
 && useradd --create-home --shell /bin/bash report

# The vmapi service, its config, its log directory and its control script.
COPY vmapi.py /opt/vmapi/vmapi.py
COPY vmapi.conf /etc/vmapi/vmapi.conf
COPY vmapi-ctl.sh /usr/local/bin/vmapi-ctl
RUN mkdir -p /var/log/vmapi \
 && chown root:root /opt/vmapi/vmapi.py /etc/vmapi/vmapi.conf /usr/local/bin/vmapi-ctl \
 && chmod 0644 /opt/vmapi/vmapi.py \
 && chmod 0644 /etc/vmapi/vmapi.conf \
 && chmod 0755 /usr/local/bin/vmapi-ctl

# The old worker and the job dispatcher.
COPY worker-v1.sh /opt/worker/worker-v1.sh
COPY dispatcher.py /opt/dispatcher/dispatcher.py
RUN chmod 0755 /opt/worker/worker-v1.sh \
 && chmod 0644 /opt/dispatcher/dispatcher.py

# The nightly report: script, input data and output directory.
COPY nightly.sh /opt/report/nightly.sh
RUN chmod 0755 /opt/report/nightly.sh \
 && mkdir -p /srv/reports/in /srv/reports/out \
 && printf 'hv01,vm-101,running\nhv01,vm-102,stopped\nhv01,vm-103,running\n' > /srv/reports/in/hv01.csv \
 && printf 'hv02,vm-201,running\nhv02,vm-202,running\nhv02,vm-203,running\n' > /srv/reports/in/hv02.csv \
 && chown -R root:report /srv/reports/in \
 && chmod 0644 /srv/reports/in/*.csv \
 && chmod 0700 /srv/reports/in \
 && chown report:report /srv/reports/out \
 && chmod 0755 /srv/reports/out

# Process 1 and the checker.
COPY box-init.sh /usr/local/sbin/box-init
COPY check.sh /usr/local/bin/check
RUN chmod 0755 /usr/local/sbin/box-init /usr/local/bin/check

EXPOSE 8080
CMD ["/usr/local/sbin/box-init"]
