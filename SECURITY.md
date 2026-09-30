# Security

The sandbox in this repository is a teaching policy jail. It decides which processes to start. It does not isolate a process that has already started, and it is not a boundary for untrusted code in production.

Use a real isolator (a container runtime, a microVM, or an OS sandbox) before an agent can run code you did not write. The chapter 02 tests describe the policy. They are not a security audit.
