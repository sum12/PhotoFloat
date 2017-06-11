/**
 * @description This module communicates with Lychee's API
 */

api = {

	path    : 'php/index.php',
	onError : null,
	photofloat : new PhotoFloat(),

}

console.log(api)

api.post = function(fn, params, callback) {

	loadingBar.show();
    var photofloat = api.photofloat;

    
	const success = (data) => {

		setTimeout(loadingBar.hide, 100)

		// Catch errors
		if (typeof data==='string' && data.substring(0, 7)==='Error: ') {
			api.onError(data.substring(7, data.length), params, data)
			return false
		}

		callback(data)

	}

	const error = (jqXHR, textStatus, errorThrown) => {

		api.onError('Server error or API not found.', params, errorThrown)

	}
    
    let object = fn.split('::')[0]
    let action = fn.split('::')[1]

    switch (object){
        case 'Session':
            switch (action){
                case 'init':
                        success({ 
                            'status' : 1,
                            'config': {
                                'login':true,
                            },
                        })
                break;
            }
        break;
        case 'Albums':
            switch (action){
                case 'get':
                    photofloat.album('root', function (albums){
                        $.each(albums.albums, function (index,theAlbum){
                                theAlbum.id=photofloat.albumHash(theAlbum, true);
                                theAlbum.title=theAlbum.path;
                                theAlbum.description='';
                                theAlbum.downloadble=1;
                                theAlbum.public=1;
                                theAlbum.password='0';
                                theAlbum.num=0;
                                theAlbum.sysdate=theAlbum.date;
                                theAlbum.thumbs = [];
                                photofloat.albumPhoto(theAlbum, function(theAlbumAgain, thePhoto){
                                    theAlbum.thumbs[0] = photofloat.photoPath(theAlbumAgain, thePhoto, 150, true);
                                }, { });
                                photofloat.albumPhoto(theAlbum, function(theAlbumAgain, thePhoto){
                                    theAlbum.thumbs[1] = photofloat.photoPath(theAlbumAgain, thePhoto, 150, true);
                                }, { });
                                photofloat.albumPhoto(theAlbum, function(theAlbumAgain, thePhoto){
                                    theAlbum.thumbs[2] = photofloat.photoPath(theAlbumAgain, thePhoto, 150, true);
                                }, { });
                            }
                        )
                                success({ 
                                    'num' : albums.albums.length,
                                    'albums': albums.albums,
                                })
                    }, error)
                break;
            }
        break;
        case 'Album':
            switch (action){
                case 'get':
                    photofloat.parseHash(params.albumID, function (album, photo, i){
                        var content = {'photos':{}, 'albums':{}}
                        console.log(album)
                        content.photos = album.photos;
                        content.albums = album.albums;
                        let prevId = ''
                        for (var index=0; index<content.photos.length; index++) {
                            thePhoto                      = content.photos[index]
                            thePhoto.id                   = photofloat.photoHash(album,thePhoto, true)
                            thePhoto.title                = thePhoto.name;
                            thePhoto.public               = 1;                         
                            thePhoto.star                 = '0';
                            thePhoto.album                = params.albumID;
                            thePhoto.sysdate              = thePhoto.dateTimeOriginal;
                            thePhoto.cameradate           = 3;
                            thePhoto.thumbUrl             = photofloat.photoPath(album, thePhoto, 150, true),

                            content[thePhoto.id]          = thePhoto;
                            thePhoto.previousPhoto        = prevId;
                            thePhoto.nextPhoto            = '';
                            if (prevId !== '') content[thePhoto.previousPhoto].nextPhoto  = thePhoto.id
                            prevId                        = thePhoto.id
                        }
                        $.each(content.albums, function (index,theAlbum){
                                theAlbum.id=photofloat.albumHash(theAlbum,true);
                                theAlbum.title=theAlbum.path;
                                theAlbum.description='';
                                theAlbum.downloadble=1;
                                theAlbum.public=1;
                                theAlbum.password='0';
                                theAlbum.num=0;
                                theAlbum.sysdate=theAlbum.date;
                                theAlbum.thumbs = [];
                                var notedalbum = theAlbum;
                                for(var tbnl=0;tbnl<3;tbnl++){
                                    photofloat.albumPhoto(theAlbum, function(theAlbumAgain, thePhoto){
                                        var pa=photofloat.photoPath(theAlbumAgain, thePhoto, 150, true);
                                        theAlbum.thumbs.push(pa);
                                    }, {})
                                }
                            }
                        )
                        success( {'id':album.id, 'content': content})
                    }, error)
                break;
            }
        break;
        case 'Photo':
            switch (action){
                case 'get':
                    console.log(params)
                    photofloat.parseHash(params.albumID+'/'+params.photoID, 
                            function (album, thePhoto, i){
                                let maxSize = 800;
                                let width = thePhoto.size[0];
                                let height = thePhoto.size[1];
                                if (width > height) {
                                    height = height / width * maxSize;
                                    width = maxSize;
                                } else {
                                    width = width / height * maxSize;
                                    height = maxSize;
                                }
                                success({
                                    'medium'     : '',
                                    'id'         : photofloat.photoHash(album,thePhoto, true),
                                    'title'      : thePhoto.name,
                                    'public'     : 1,
                                    'star'       : '0',
                                    'album'      : params.albumID,
                                    'sysdate'    : thePhoto.dateTimeOriginal,
                                    'cameradate' : 3,
                                    'url'        : photofloat.photoPath(album, thePhoto, maxSize, false),
                                })
                            })
                break;
            }
        break;
    }

}
