/**
 * Calculate distance between two coordinates using Haversine formula
 * @param lat1 - Latitude of first point
 * @param lon1 - Longitude of first point
 * @param lat2 - Latitude of second point
 * @param lon2 - Longitude of second point
 * @returns Distance in kilometers
 */
export function calculateDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371 // Radius of the Earth in kilometers
  const dLat = toRadians(lat2 - lat1)
  const dLon = toRadians(lon2 - lon1)

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(lat1)) *
      Math.cos(toRadians(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2)

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  const distance = R * c

  return distance
}

/**
 * Convert degrees to radians
 * @param degrees - Angle in degrees
 * @returns Angle in radians
 */
function toRadians(degrees: number): number {
  return degrees * (Math.PI / 180)
}

/**
 * Calculate distance from user location to news location
 * @param userLat - User latitude
 * @param userLon - User longitude
 * @param newsLat - News latitude (can be string or null)
 * @param newsLon - News longitude (can be string or null)
 * @returns Distance in kilometers, or null if coordinates are invalid
 */
export function calculateNewsDistance(
  userLat: number | null,
  userLon: number | null,
  newsLat: string | null,
  newsLon: string | null
): number | null {
  if (
    userLat === null ||
    userLon === null ||
    newsLat === null ||
    newsLon === null
  ) {
    return null
  }

  const lat2 = parseFloat(newsLat)
  const lon2 = parseFloat(newsLon)

  if (isNaN(lat2) || isNaN(lon2)) {
    return null
  }

  return calculateDistance(userLat, userLon, lat2, lon2)
}
