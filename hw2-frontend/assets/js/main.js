
function uploadPhoto(){
    var file = document.getElementById("photo-upload").files[0];
    if (file == undefined) {
        document.getElementById('upload-msg').innerHTML = "Please select an image.";
    }
    else{
        var filename = file.name;
        var customLabel = document.getElementById("custom-label").value;

        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = function() {
            const base64Data = this.result.replace(/^data:(.*;base64,)?/, '');
            // console.log(base64Data);

            console.log(file);

            sdk.uploadBucketKeyPut(
                {'x-amz-meta-customLabels': customLabel,
                'key': filename, 
                'bucket': 'photos-cf-b-2'}, 
                base64Data,
                {"headers":{"Content-Type": file.type}}
            )
            .then((response) =>{
            document.getElementById('upload-msg').innerHTML = "Succeessfully uploaded photo.";
            document.getElementById('custom-label').innerHTML = "";
            })
            .catch((error) => {
            console.log("error", error);
            });
        };
    }
}

function recognitionSpeech() {

    console.log('micro button pressed');

    const recognition = new webkitSpeechRecognition(); 
    recognition.lang = 'en-US';
  
    recognition.onstart = () => {
      console.log('Speech recognition started'); 
    };
  
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript.trim(); 
      document.getElementById('search-msg').value = transcript; 
      console.log('Speech recognition result:', transcript); 
    };
  
    recognition.onend = () => {
      console.log('Speech recognition ended'); 
    }
  
    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
    };
  
    recognition.start(); 
}



function searchPhoto(){

    const searchInput = document.getElementById("search-msg").value;

    if (searchInput.length==0){
        document.getElementById('search-msg').innerHTML = "Please Enter A Keyword";
    }
    else{

        sdk.searchGet(
            {'q': searchInput},
            {},
            {}
        )
        .then((response) =>{
            console.log("received "+searchInput);

            console.log(response.data.results)

            if (response.data.results.length != 0){
                document.getElementById('viewer').innerHTML = "";
                response.data.results.forEach(element => {
                    console.log(element.url);
                    fetch(element.url)
                    .then(res => res.blob())
                    .then(blob => {
                        blob.text().then((data) => {
                            var htmlPhoto = '<img style="width:128px;height:128px;" src="data:image/jpg;base64,' + data + '"><br></br>';
                            $('#viewer').append(htmlPhoto);
                        });
                    });
                });
                document.getElementById('search-response').innerHTML = "";
            }
            else{
                document.getElementById('search-response').innerHTML = "No Matched Photo in Album";
                document.getElementById('viewer').innerHTML = "";
            }

        })
        .catch((error) => {
            console.log("error", error);
        });
    }


}

