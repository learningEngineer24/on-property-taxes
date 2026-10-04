# Alameda County Assessor Use Codes — Official Lookup

**Source (official):** https://propinfo.acgov.org/UseCodeList/ (Assessor's Property Search site)
Also referenced from https://www.acassessor.org/use-codes/.

**Caveat from the Assessor:** "The Assessor's Use Code has been designed for use by this
department for the purpose of appraising properties for assessment purposes only. ...
information concerning property characteristics is maintained solely for assessment purposes
and is not continuously updated by the assessor." (Revenue and Tax Code Sec. 408.3(d))

**Coverage in our parcel data (184k rows scanned, partial download):** 146 distinct UseCode
values; all top-15 values below map cleanly to this table. 167 parcels had a null UseCode.

## Observed top UseCodes in parcels (labeled, official)

| UseCode | Count (partial) | Official description |
|---------|-----------------|----------------------|
| 1100 | 119,380 | Single family residential homes used as such |
| 2200 | 6,971 | Double or duplex type - two units |
| 7700 | 4,813 | Multiple residential building of 5 or more units |
| 0300 | 4,668 | Exempt Public Agency (listed as "300") |
| 2500 | 3,961 | 2 units, lesser quality than 2200 or unknown legal |
| 2400 | 3,569 | Four living units; e.g. fourplex or triplex w/SFR |
| 1000 | 3,479 | Vacant residential land, zoned 4 units or less |
| 1500 | 3,400 | Townhouse - Planned Development |
| 1800 | 2,970 | SFR - Planned Development Tract with Common Area |
| 2100 | 2,924 | Two, three or four single family homes |
| 2300 | 2,168 | Triplex; double or duplex with single family home |
| 7390 | 1,840 | Condominium Common Area or use |
| 3200 | 1,755 | Store/Office with Apts/Lofts |
| 1200 | 1,707 | Single family res home with non-economic 2nd unit |
| 3100 | 1,629 | Single-tenant Retail Store |

Note: `7390` (condo common area) and `1190`/`1590`/`1690`/`1890`/`7790`/`3990`/`4191`/`9491`
"Common Area or use" codes are the **stacked-condo / common-area parcels** flagged in the plan
— many map to the same building footprint.

## Full table (transcribed verbatim from propinfo.acgov.org/UseCodeList/)

Series are determined by the first digit (second digit narrows within series).
"R&T 402.1" = Revenue & Taxation Code §402.1 (restricted/partially complete property rules).

### 0x — Exempt, Not Assessed by County, Mobile Homes and Tracts
| Code | Description |
|------|-------------|
| 300 | Exempt Public Agency |
| 400 | Property leased to a public utility |
| 500 | Property owned by a public utility |
| 600 | Mobile home on SFR/rural land |
| 700 | Mobile home in a mobile home park |
| 750 | Floating home |
| 800 | Vacant residential tract lot |
| 840 | Tract land, R&T 402.1 |
| 900 | Partially complete residential tract home |
| 940 | Tract residential PC, R&T 402.1 |

### 1x — Single Family Residential
| Code | Description |
|------|-------------|
| 1000 | Vacant residential land, zoned 4 units or less |
| 1040 | Vacant residential land, R&T 402.1 |
| 1100 | Single family residential homes used as such |
| 1101 | Medical-Residential Care Facility (SFR/Res Imps) |
| 1120 | Residential Imps on Commercial Land |
| 1130 | Residential Imps on Industrial Land |
| 1140 | Single family residential home, R&T 402.1 |
| 1150 | Historical residential |
| 1160 | Land Trust - residential improve on leased land |
| 1166 | Land Trust - common area |
| 1190 | Single family residential (tract) common area or use |
| 1200 | Single family res home with non-economic 2nd unit |
| 1201 | SFR with junior accessory dwelling unit |
| 1300 | Single Family Res home with slight commercial/ind |
| 1400 | Single Family Res - Duet Style |
| 1420 | Single Family Res - Duet Style, First Sale |
| 1430 | Single Family Res - Duet Style, R&T 402.1, First Sale |
| 1440 | Single Family Res - Duet Style, R&T 402.1 |
| 1500 | Townhouse - Planned Development |
| 1505 | Townhouse Style - Condominium |
| 1520 | Townhouse - Planned Development, First Sale |
| 1525 | Townhouse Style - Condominium, First Sale |
| 1530 | Townhouse - Planned Development, R&T 402.1, First Sale |
| 1535 | Townhouse Style - Condominium, R&T 402.1, First Sale |
| 1540 | Townhouse - Planned Development, R&T 402.1 |
| 1545 | Townhouse Style - Condominium R&T 402.1 |
| 1590 | Townhouse - Planned Development, Common Area or use |
| 1595 | Townhouse Style - Condominium, Common Area or use |
| 1600 | SFR Detached Site Condominium |
| 1620 | SFR Detached Site Condominium, First Sale |
| 1630 | SFR Detached Site Condominium, R&T 402.1, First Sale |
| 1640 | SFR Detached Site Condominium, R&T 402.1 |
| 1690 | SFR Detached Site Condominium, Common Area or use |
| 1700 | Single family res home converted to boarding house |
| 1800 | SFR - Planned Development Tract with Common Area |
| 1820 | SFR - Planned Development Tract, First Sale |
| 1830 | SFR - Planned Development Tract, R&T 402.1, First Sale |
| 1840 | SFR - Planned Development Tract, R&T 402.1 |
| 1850 | Duet/Duplex/Triplex - Planned Development Tract w/Common Area |
| 1860 | Duet/Duplex/Triplex - Planned Development Tract, R&T 402.1 |
| 1890 | SFR - Planned Development Tract, Common Area or use |
| 1900 | SFR - Manufactured Home (MH on permanent foundation) |
| 1901 | Single family modular built off site |
| 1950 | Non-Condo Live/Work |

### 2x — Multiple Residential, 2–4 Units and Mobile Homes
| Code | Description |
|------|-------------|
| 2100 | Two, three or four single family homes |
| 2200 | Double or duplex type - two units |
| 2300 | Triplex; double or duplex with single family home |
| 2400 | Four living units; e.g. fourplex or triplex w/SFR |
| 2440 | Four residential living units, R&T 402.1 |
| 2500 | 2 units, lesser quality than 2200 or unknown legal |
| 2501 | 2 units, SFR with attached accessory dwelling unit |
| 2502 | 2 units, SFR with detached accessory dwelling unit |
| 2541 | 2 units, SFR with attached accessory dwelling unit, R&T 402.1 |
| 2542 | 2 units, SFR with detached accessory dwelling unit, R&T 402.1 |
| 2600 | 3 units, lesser quality than 2300 or unknown legal |
| 2700 | 4 units, lesser quality than 2400 or unknown legal |
| 2800 | Res property of 2,3 or 4 units with rooming house |
| 2900 | More than 1 mobile home, or M/H w/other res units |

### 3x — Commercial (see also 8x & 9x)
| Code | Description |
|------|-------------|
| 3000 | Vacant commercial land (may include misc. imps) |
| 3100 | Single-tenant Retail Store |
| 3120 | Commercial Imps on Residential Land |
| 3200 | Store/Office with Apts/Lofts |
| 3300 | Miscellaneous improved commercial |
| 3400 | Department store |
| 3500 | National Chain Retailer |
| 3600 | Restaurant - small or in-line walk-in restaurant / cafe |
| 3605 | Restaurant - Free-Standing |
| 3610 | Restaurant - Fast Food |
| 3620 | Bar / Bar with limited food service |
| 3700 | Shopping Center-NBHD/Grocery or Retail anchor |
| 3701 | Shopping Center-Community |
| 3702 | Shopping Center-Regional Mall |
| 3703 | Shopping Center-NBHD without anchor (strip mall) |
| 3704 | Shopping Center-Power Center |
| 3705 | Shopping Center + Residential + Other |
| 3800 | Supermarket |
| 3900 | Condominium-commercial retail |
| 3990 | Condominium-commercial retail, common area or use |

### 4x — Industrial
| Code | Description |
|------|-------------|
| 4000 | Vacant industrial land (may include misc. imps) |
| 4100 | Warehouse |
| 4101 | Condominium-industrial |
| 4102 | Warehouse-Self Storage |
| 4103 | Warehouse-Cold Storage |
| 4191 | Condominium-industrial, common area or use |
| 4200 | Industrial Light/Manufacturing |
| 4201 | Industrial Flex/R&D |
| 4202 | Data Center |
| 4205 | Advanced Tech manufacturing with R&D/Large-scale |
| 4240 | Live-Work condominium, R&T 402.1 |
| 4300 | Heavy industrial |
| 4400 | Misc. industrial (improved); no other ind code |
| 4500 | Nurseries |
| 4600 | Quarries, Sand and Gravel |
| 4601 | Landfill |
| 4700 | Salt Ponds |
| 4800 | Terminals, trucking and distribution |
| 4900 | Wrecking yards |

### 5x — Rural
| Code | Description |
|------|-------------|
| 5000 | Vacant rural-res homesites, may incl misc. imps |
| 5100 | Improved rural-residential homesite. |
| 5200 | One or more mobile homes on rural home site. |
| 5300 | Rural property used for agriculture and/or commercial <10 acre |
| 5400 | Rural property with industrial use |
| 5500 | Rural property used for agriculture and/or commercial 10+ acre |
| 5600 | Rural property in transition to a higher use |
| 5700 | Vacant rural land, not usable even for agriculture |
| 5800 | Improved rural land, non-renewal Williamson Act |
| 5900 | Vacant rural land, non-renewal Williamson Act |

### 6x — Institutional
| Code | Description |
|------|-------------|
| 6000 | Vacant land necessary part of institutional prop. |
| 6001 | Government owned property - vacant land |
| 6100 | Government owned property - improved |
| 6200 | Secured PI |
| 6300 | Golf course |
| 6400 | School |
| 6500 | Cemetery |
| 6590 | Cemetery - Exempt |
| 6600 | Church |
| 6700 | Other institutional property |
| 6800 | Lodgehall and/or clubhouse |
| 6850 | Historical commercial |

### 7x — Multiple Residential, 5 or more units
| Code | Description |
|------|-------------|
| 7000 | Vacant apartment land, capable of 5 or more units |
| 7040 | Vacant apartment land, R&T 402.1 |
| 7090 | Vacant apartment common area or use |
| 7100 | Five or more single family res homes |
| 7200 | Residential property converted to 5 or more units |
| 7300 | Condominium - single residential living unit |
| 7301 | Condominium - residential live/work unit |
| 7302 | Condominium - urban res unit above retail/office |
| 7305 | Condominium - townhouse style |
| 7320 | Condominium - single res unit, first sale |
| 7321 | Condominium - res live/work unit, first sale |
| 7322 | Condominium - urban res unit above, first sale |
| 7325 | Condominium - townhouse, first sale |
| 7330 | Condominium - single res unit, R&T 402.1, First Sa |
| 7335 | Condominium - townhouse, R&T 402.1, First Sale |
| 7340 | Condominium - single res unit, R&T 402.1 |
| 7341 | Condominium - res live/work unit, R&T 402.1 |
| 7342 | Condominium - urban res R&T 402.1 |
| 7345 | Condominium - Townhouse R&T 402.1 |
| 7390 | Condominium Common Area or use |
| 7391 | Condominium - res live/work, common area or use |
| 7392 | Condominium - urban res unit above, common area or use |
| 7395 | Condominium - townhouse, common area |
| 7400 | Cooperatives (divided) |
| 7430 | Cooperatives (undivided) |
| 7500 | Restricted residential income property |
| 7600 | Fraternities and sororities |
| 7700 | Multiple residential building of 5 or more units. |
| 7701 | Assisted Living Apartments |
| 7705 | Multiple-Res building of 5 or more units + commercial units |
| 7706 | Multi-Res building of 5 or more units R&T 402.1 + commercial |
| 7790 | Apartment Common Area or use |
| 7800 | Residential high-rise (7 or more stories) |
| 7900 | Church Home |

### 8x — Improved Commercial
| Code | Description |
|------|-------------|
| 8000 | Car wash |
| 8100 | Commercial repair garage |
| 8200 | Automobile dealership |
| 8300 | Parking lot |
| 8400 | Parking garage |
| 8500 | Service Stations |
| 8600 | Funeral home |
| 8700 | Nursing/Custodial Care Facility |
| 8800 | Hospital (general) |
| 8801 | Medical clinic/outpatient surgery |
| 8802 | Skilled Nursing Facility |
| 8900 | Hotel |
| 8901 | SRO Hotel |

### 9x — Improved Commercial
| Code | Description |
|------|-------------|
| 9000 | Motel |
| 9100 | Mobile home park parcel with improvements |
| 9200 | Bank |
| 9300 | Medical - Dental building |
| 9301 | Veterinarian Office |
| 9400 | One to five story office building |
| 9401 | Condominium-office |
| 9405 | Condominium-Medical office |
| 9491 | Condominium-office, common area or use |
| 9500 | Over five story office building |
| 9600 | Bowling alley |
| 9700 | Walk-in theater |
| 9800 | Drive-in theater |
| 9801 | Winery |
| 9802 | Winery, including retail/event center |
| 9900 | Other recreational activity, e.g. rinks, stadiums |
| 9901 | Boat berth privately owned |
| 9902 | Subsurface right-oil, gas, mineral |
| 9905 | Fitness Center/Health Club/Gym |
| 9910 | Museums, Historical Societies/Clubs |
| 9999 | P19 - Intergenerational Transfers |

## Analysis notes

- **Residential grouping (suggested):** 1x (SFR + variants), 2x (2–4 unit), 7x (5+ unit), plus
  0x/5x rural residential. Commercial = 3x/8x/9x; industrial = 4x; institutional = 6x.
- **"First Sale" codes** (1420/1520/1600-series/7320-series etc.) = new-construction first
  sales — useful for the market-value model (transfer-implied values).
- **"R&T 402.1" codes** = restricted/partially complete — treat assessed values with care.
- **9999 (P19 intergenerational transfers)** = Prop 19 parent-child transfers — excluded from
  Prop 13 reassessment; these are NOT arm's-length market transfers. Filter out of the
  market-value model's recent-transfer cohort.
- **ADU codes** (1201/2501/2502/2541/2542) are new-ish; presence varies by when the assessor
  adopted them.
