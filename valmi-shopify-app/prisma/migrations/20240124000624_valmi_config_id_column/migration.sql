/*
  Warnings:

  - The primary key for the `Valmiconf` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - Added the required column `id` to the `Valmiconf` table without a default value. This is not possible if the table is not empty.

*/
-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_Valmiconf" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "host" TEXT NOT NULL,
    "writeKey" TEXT NOT NULL
);
INSERT INTO "new_Valmiconf" ("host", "writeKey") SELECT "host", "writeKey" FROM "Valmiconf";
DROP TABLE "Valmiconf";
ALTER TABLE "new_Valmiconf" RENAME TO "Valmiconf";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
