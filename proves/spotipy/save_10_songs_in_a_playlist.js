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

const tracksUri = [
  'spotify:track:5hGIRMjtrTpdMdTrZv4lh1','spotify:track:0Q3oC2GIFVgGNxjNYCTTio','spotify:track:0C4ejWmOTMv8vuYj85mf8m','spotify:track:2IuepwvMuaTlNN0DSgVsCg','spotify:track:0rfbvwLPBLBsEd4Bxz8IVb','spotify:track:0glMVNiX5kjmNkbdkvDFzk','spotify:track:3Vtt2oOW5USQbG23M52nGR','spotify:track:78YZdpDXVJozZzcUE4JZa4','spotify:track:5O1qLn6D0EJTba2s1ZSb2T','spotify:track:66IPnrM0cVCPtxDfyYsWlI'
];

async function createPlaylist(tracksUri){
  const { id: user_id } = await fetchWebApi('v1/me', 'GET')
  
  const playlist = await fetchWebApi(
    `v1/users/${user_id}/playlists`, 'POST', {
      "name": "My recommendation playlist",
      "description": "Playlist created by the tutorial on developer.spotify.com",
      "public": false
  })
  
  await fetchWebApi(
    `v1/playlists/${playlist.id}/tracks?uris=${tracksUri.join(',')}`,
    'POST'
  );

  return playlist;
}

const createdPlaylist = await createPlaylist(tracksUri);
console.log(createdPlaylist.name, createdPlaylist.id);