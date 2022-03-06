| ![Sigma Telecom](/docs/logo-sigma.svg) |
| -------------------------------------- |
|                                        |

# Sigma Telecom - RDS

Distributed monitoring platform

Name nodes as following syntax

- Master: rds-m-x
- Satellites: rds-s-y

Satellite MDU port are Services

See [docs](/docs) folder for more information

```mermaid
graph LR;
  rds-m-1-->rds-s-1;
  rds-m-1-->rds-s-2;

  rds-s-1-->mdu1_p1;
  rds-s-1-->mdu1_p2;
  rds-s-1-->mdu1_p3;
  rds-s-1-->mdu1_p4;

  rds-s-2-->mdu2_p1;
  rds-s-2-->mdu2_p2;
  rds-s-2-->mdu2_p3;
  rds-s-2-->mdu2_p4;

  mdu1_p1-->mdu1_p1_rdu1-->mdu1_p1_rdu2-->mdu1_p1_rdu3;
  mdu1_p2-->mdu1_p2_rdu1-->mdu1_p2_rdu2-->mdu1_p2_rdu3-->mdu1_p2_rdu4-->mdu1_p2_rdu5;
  mdu1_p3-->mdu1_p3_rdu1;
  mdu1_p4-->mdu1_p4_rdu1-->mdu1_p4_rdu2-->mdu1_p4_rdu3;

  mdu2_p2-->mdu2_p2_rdu1-->mdu2_p2_rdu2;

  style rds-m-1 color:#000,fill:#5f5,stroke:#050,stroke-width:1px;

  style rds-s-1 color:#f55,fill:#5f5,stroke:#050,stroke-width:1px;
  style rds-s-2 color:#f55,fill:#5f5,stroke:#050,stroke-width:1px;

  style mdu1_p1 color:#fff,fill:#55f,stroke:#005,stroke-width:1px;
  style mdu1_p2 color:#fff,fill:#55f,stroke:#005,stroke-width:1px;
  style mdu1_p3 color:#fff,fill:#55f,stroke:#005,stroke-width:1px;
  style mdu1_p4 color:#fff,fill:#55f,stroke:#005,stroke-width:1px;

  style mdu2_p1 color:#fff,fill:#55f,stroke:#005,stroke-width:1px;
  style mdu2_p2 color:#fff,fill:#55f,stroke:#005,stroke-width:1px;
  style mdu2_p3 color:#fff,fill:#55f,stroke:#005,stroke-width:1px;
  style mdu2_p4 color:#fff,fill:#55f,stroke:#005,stroke-width:1px;
```

---

## Node Installation

On every node clone this repository and follow specific node type instructions.

```
git clone https://gitlab.com/itaum/sigma-rds /tmp/sigma-rds
cd /tmp/sigma-rds
git checkout development
```

### Specific instructions for:

- [Master Nodes](docs/setup_master_debian.md)
- [Satellite Nodes](docs/setup_satellite_debian.md)

---

## Usage

Go to Master WebUI -> Director Module Menu:

- Add new Host Template if you don't have one yet
- Add new Service Template if you don't have one yet
- Add new Host and children Service
- Deploy changes
