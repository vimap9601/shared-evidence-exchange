# Google Drive Setup

1. Create a private root folder.
2. Initialize the SEEP folder structure locally.
3. Upload the structure to Drive.
4. Verify that each model's connector can read the root folder.
5. Test whether each connector can create or upload files.
6. If write access is asymmetric, designate a writable outbound folder for the capable model and a human upload step for the other.
7. Do not rely on duplicate filenames.
8. Keep numbered exchange files immutable.
9. Use a completion marker in `40_RECONCILED_OUTPUT`.

Google Drive is storage, not an event bus. Without scheduled agents or an API broker, models do not automatically know another file appeared.
