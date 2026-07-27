# Google Drive Setup

1. Create a private root folder.
2. Initialize the SEEP folder structure locally.
3. Upload the structure and primary evidence to Drive.
4. Verify that each model's connector can recursively discover the root folder and nested folders.
5. Generate the evidence manifest outside Drive or through a capable agent, then store it in `01_GOVERNING_STATE`.
6. Test representative PDFs, images, archives, native files, and large files. Record unsupported formats and search limitations.
7. Test whether each connector can create or upload files.
8. If write access is asymmetric, designate a writable outbound folder for the capable model and a human upload step for the other.
9. Do not rely on duplicate filenames. Use paths and hashes.
10. Keep numbered exchange files immutable.
11. Use a completion marker in `40_RECONCILED_OUTPUT`.

Google Drive is storage, not an event bus. Without scheduled agents or an API broker, models do not automatically know another file appeared. Drive search results may also be partial, so connector search alone is not proof that evidence is absent.
