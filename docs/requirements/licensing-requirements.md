# Licensing Requirements

Status: DRAFT, written 26 November 2026 at John's request, for John's approval. Nothing here is approved until John says so. Authority: the [SSOT](../SSOT.md). If this document disagrees with the SSOT, this document is corrected. Nothing here is legal advice. A licence class records what a page said on the date given, and a person with legal knowledge should confirm anything before the project is published or deployed.

## 1. Purpose and scope

This document owns the licence of everything the project uses or ships: datasets, models, word lists, libraries and container images, and what may be committed to the public repository or deployed. Data Section 4 and SR-01 to SR-11 own each data source and its access. Project-Wide ET-03 asks for the third-party register. Deployment and Operations owns where and how the system runs.

John asked that every dataset the project imports has a permissive licence. **It does not today** (Section 3). LC-03 states the goal, and its test is expected to fail until it is met.

## 2. Licence classes

`src/earnings/licensing.py` holds the classes. Data may be deployed or published only when its class is `permissive` or `public-information`. `share-alike` data is open but not permissive. A library or image may be used in a deployed system when it is `permissive`, or `weak-copyleft` and used unchanged.

## 3. What the project uses, as checked on 26 November 2026

| Item | What the page said | Class | Consequence |
|---|---|---|---|
| SEC EDGAR data (EPS, filing times, fundamentals, identifiers) | "All Government-created content on sec.gov and EDGAR public filing content are free to access and reuse." Cite the SEC. At most 10 requests a second, with a declared user agent | public-information | Deployable, citing the SEC |
| Index membership, `fja05680/sp500` | MIT | permissive | Deployable with the notice. The underlying index is S&P's; rights in the index itself were not checked |
| Wikipedia removal names and reasons | CC BY-SA 4.0 | share-alike | Not permissive. Needs attribution and share-alike, or leaving the reasons out of a deployed copy |
| Transcripts, `kurry/sp500_earnings_transcripts` | MIT in the metadata, and "For research and educational use only." No origin for the text | unclear | Not deployable. Publishing the text is not covered |
| Prices and consensus through yfinance | yfinance's code is Apache-2.0. Yahoo's terms bar access "using any automated means" without "express, prior permission", use of its data "to create any database", commercial use and redistribution | restricted | Not deployable. **The daily consensus capture and the price load appear to conflict with these terms** (LC-08) |
| Finnhub free key | Personal use; no sharing of data or derived results | restricted | Not deployable. Not used by the primary route |
| `ProsusAI/finbert` weights (approved, C-54) | CC BY-NC-SA 4.0, "restricts commercial use". Trained on Financial PhraseBank (CC BY-NC-SA 3.0) and a Reuters corpus under NIST access terms | non-commercial | Usable for a non-commercial dissertation. Not permissive |
| Loughran and McDonald word list (approved, C-14) | "free for use in academic research"; commercial licences from the authors | restricted | Not permissive |
| Redis 7.4.12 container image | Redis 7.4: RSALv2 or SSPLv1. Redis 7.2 and earlier: BSD 3-Clause | source-available | Not open source. Valkey (BSD 3-Clause) or Redis 7.2 would remove this |
| Python packages in `requirements.lock` | MIT, BSD, Apache-2.0, PSF; `psycopg` LGPL 3.0 only; `certifi` MPL 2.0 | permissive or weak-copyleft | Allowed |
| PostgreSQL and Python base images | Not fetched on this date | permissive; unclear | To be read before deployment |

## 4. Replacements looked for

| For | What was found | Verdict |
|---|---|---|
| Transcripts | Web search found only sets labelled MIT with the same underlying text, and a CC-BY question-answer set that was not shown to cover this universe or period. A US court held one distribution of an earnings call recording fair use (Swatch v. Bloomberg, 2d Cir. 2014); that concerns audio in one circuit and gives no licence for these texts | **No permissively licensed replacement found** |
| Prices with delisted companies | No source found that is free, current, openly licensed and covers delisted names. Some Kaggle sets are labelled CC0 but end in 2020 or have doubtful provenance | **No replacement found** |
| FinBERT | `empiriolabsai/finance-sentiment`: Apache-2.0, base model MIT. The data used to fine-tune it is not stated, and its evaluation is the vendor's own. `yiyanghkust/finbert-tone` states no licence | A candidate only. Changing it departs from the proposal's FinBERT and needs its own evaluation |
| Word list | None checked | Open |

## 5. Requirements

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| LC-01 | Must | Every library pinned in the lock file, every container image, every model and every word list has a row in the third-party register with its version, licence, class, evidence and the date checked. Every dataset has a source register row with a class. | A pinned package or an image with no register row fails the test. | Project-Wide ET-03; Data SR-01 |
| LC-02 | Must | The licence classes are a fixed list, and only the classes in Section 2 may be deployed. | A register row with a class outside the list fails the test. | Data SR-03 |
| LC-03 | Must | Every dataset the project imports has a class that may be deployed. | No dataset in the source register has a class that may not be deployed. | John's request of 26 November 2026 |
| LC-04 | Must | A deployment bundle is described by a manifest of dataset ids, and it is refused when it names a dataset that is unregistered or may not be deployed. | A manifest naming a restricted, unclear, share-alike or unregistered dataset is refused. | Data SR-03; Deployment and Operations DP-13 |
| LC-05 | Must | The attribution notices are generated from the registers and committed. | The committed notices file equals the generated one. | Project-Wide ET-03 |
| LC-06 | Must | The public repository holds no real data from a dataset that may not be deployed, beyond a quotation limit recorded for that source. | No committed fixture holds real text or values from a source that may not be deployed. | Data SR-03, SR-11; Deployment and Operations DP-10 |
| LC-07 | Must | Every outside source named in the code has a source register row. | A source name in a client module with no register entry fails the test. | Data SR-01 |
| LC-08 | Must | No job collects from a source whose terms bar automated collection. | No scheduled job uses a source whose terms bar automated collection. | Section 3; Data SR-07 |
| LC-09 | Must | For each model, the licence of the weights and of the training data are both recorded. | Every model row names the licence of its training data. | Project-Wide ET-03; Feature Engineering FE-05 |
| LC-10 | Should | Licence evidence is checked again no more than 90 days before any deployment or publication. | A row checked more than 90 days before the date given is listed as stale. | Section 1 |
| LC-11 | Must | Every library and container image used in a deployed system is permissive, or weak-copyleft and used unchanged. | No library or image in use has any other class. | Deployment and Operations DP-01; John's request of 26 November 2026 |

## 6. Decisions this document leaves to John

Listed as D-49 in the [decision log](../decision-log.md). Until they are made, the tests for LC-03, LC-06, LC-08 and LC-11 are expected failures: they report the gap and do not hide it.

## 7. Pages read

SEC privacy page and webmaster FAQ; the Hugging Face card of the transcript set; Yahoo Terms of Service (read to part of section 12); the yfinance README; `ProsusAI/finbert` and `empiriolabsai/finance-sentiment` model pages and the `mmBERT-base` page; Financial PhraseBank dataset page; the Loughran and McDonald page; the Redis licence page; the Valkey site and repository; package metadata in the project image. Web search results were used only to look for alternatives, and are not relied on for any licence statement. All on 26 November 2026.
