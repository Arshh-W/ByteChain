import {
  UploadCloud,
  ScanFace,
  FileSearch,
  Link2,
  BadgeCheck,
  LayoutDashboard,
} from "lucide-react";

export const NAV_ITEMS = [
  { key: "upload", label: "Upload", icon: UploadCloud },
  { key: "analysis", label: "Analysis", icon: ScanFace },
  { key: "results", label: "Results", icon: FileSearch },
  { key: "blockchain", label: "Blockchain", icon: Link2 },
  { key: "certificate", label: "Certificate", icon: BadgeCheck },
  { key: "dashboard", label: "Dashboard", icon: LayoutDashboard },
];

export const RECENT_UPLOADS = [
  { name: "interview_portrait.jpg", meta: "2 hours ago" },
  { name: "news_photo.png", meta: "1 day ago" },
  { name: "press_image.webp", meta: "2 days ago" },
];

export const PIPELINE_STEPS = [
  { label: "Reading Image", status: "done" },
  { label: "Face Detection", status: "done" },
  { label: "Feature Extraction", status: "active" },
  { label: "Deepfake Classification", status: "pending" },
  { label: "Integrity Verification", status: "pending" },
];

export const KEY_FINDINGS = [
  { label: "Face Manipulation", value: 82 },
  { label: "Image Consistency", value: 76 },
  { label: "Metadata Integrity", value: 69 },
  { label: "Lighting Consistency", value: 21 },
];

export const NOTES = [
  "Inconsistent facial micro-expressions detected",
  "Image consistency anomaly detected",
  "Metadata integrity could not be confirmed",
  "Lighting pattern irregularities",
];

export const TREND_DATA = [
  { day: "May 18", value: 6 },
  { day: "May 19", value: 9 },
  { day: "May 20", value: 7 },
  { day: "May 21", value: 12 },
  { day: "May 22", value: 10 },
  { day: "May 23", value: 15 },
  { day: "May 24", value: 13 },
];

export const DIST_DATA = [
  { name: "Deepfake", value: 66.7, color: "#fb7185" },
  { name: "Authentic", value: 33.3, color: "#22d3ee" },
];

export const RECENT_VERIFICATIONS = [
  {
    name: "interview_portrait.jpg",
    meta: "May 24, 03:19 PM",
    score: "24.8%",
    tone: "rose",
  },
  {
    name: "tech_portrait.png",
    meta: "May 24, 11:10 AM",
    score: "91.3%",
    tone: "emerald",
  },
  {
    name: "news_photo.webp",
    meta: "May 22, 08:45 AM",
    score: "16.6%",
    tone: "rose",
  },
  {
    name: "event_photo.jpg",
    meta: "May 22, 04:22 PM",
    score: "87.3%",
    tone: "emerald",
  },
];
