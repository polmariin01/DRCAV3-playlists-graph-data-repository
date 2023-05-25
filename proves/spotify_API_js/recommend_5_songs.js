// Authorization token that must have been created previously. See : https://developer.spotify.com/documentation/web-api/concepts/authorization
const token = 'BQAz4X02rK5fv76iObkcghFZWLOADCs_aJJC3ki2WRYqL2wrjgzUaDoTxUME1AdDeBLbkSuFIkRh7cNSHWWnZQnLobQJd5eU1-Qg_E15W2ZVs2Gc0ZIZxDBXlKMVjVKFbltNnWK25S8rtr07O_6Qit83NoHwjOtNSBScTq0o9zpQI1bky2AWZQEaFgH7BfIXgd6h_Od9obtsGJcz3oNbmHqBrTP60AoyPU1Brl92RNHjZSzqJ9kjkTSExm2hjBaFv77yxJYRciz5P5CzeMhUcFO7eZL9';
async function fetchWebApi(endpoint, method, body) {
  const res = await fetch(`https://api.spotify.com/${endpoint}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    method,
    body:JSON.stringify(body)
  });
  return await res.json();
}

const topTracksIds = [
  '5hGIRMjtrTpdMdTrZv4lh1','0C4ejWmOTMv8vuYj85mf8m','0rfbvwLPBLBsEd4Bxz8IVb','3Vtt2oOW5USQbG23M52nGR','5O1qLn6D0EJTba2s1ZSb2T'
];

async function getRecommendations(){
  // Endpoint reference : https://developer.spotify.com/documentation/web-api/reference/get-recommendations
  return (await fetchWebApi(
    `v1/recommendations?limit=5&seed_tracks=${topTracksIds.join(',')}`, 'GET'
  )).tracks;
}

const recommendedTracks = await getRecommendations();
console.log(
  recommendedTracks.map(
    ({name, artists}) =>
      `${name} by ${artists.map(artist => artist.name).join(', ')}`
  )
);