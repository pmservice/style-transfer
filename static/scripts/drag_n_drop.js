var styleImage = null
var baseImage = null
var resultImage = null
var definition_uid = null
var experimentId = null
var runId = null

var dragHandler = function(evt){
    evt.preventDefault();
};

var dropHandler = function(evt){
    evt.preventDefault();
    var files = evt.originalEvent.dataTransfer.files;
    file = files[0];

    elId = evt.currentTarget.id
    $("#" + elId).html("<img src='/staticImages/loading_spinner.gif' style='height: 40%; width: 40%; object-fit: contain; margin-bottom: 8px;' />");

    if(elId == 'styleImage')
        styleImage = file.name;
    else if(elId == 'baseImage')
        baseImage = file.name;
    else
        throw 'Unexpected target id: ' + elId;

    send_image(file)
    .then(function () {
        $("#uploadImagesErrors").attr("style", "display: none");
        console.log('Successfully uploaded image.');

        if (styleImage != null && baseImage != null)
            $("#runButton").prop("disabled", false);

        $("#" + elId).html("<img src='/images/" + encodeURI(file.name) + "' class=\"droppedImage\" />");
    }).catch(function (error) {
        error = error.responseText;
        var errorMsg = 'Failed while uploading image: ' + JSON.stringify(error);
        $("#uploadImagesErrors").attr("style", "display: block");
        $("#uploadImagesErrors").html(errorMsg);
        throw errorMsg;
    });
};

var dropHandlerSet = {
    dragover: dragHandler,
    drop: dropHandler
};

var disable_divs = function(jQueryElName, classNames) {
    $(jQueryElName).on({});
    $(jQueryElName).prop('class', classNames)
}

var enable_divs = function(jQueryElName, classNames, handlers) {
    $(jQueryElName).on(handlers);
    $(jQueryElName).prop('class', classNames)
}

$(".droparea").on(dropHandlerSet);


var clean_env_clicked = function(evt){
    // zablokuj ekran
    clean_env(styleImage, baseImage, resultImage, definition_uid, experimentId, runId)
    .then(function () {
        console.log('Successfully cleaned environment.')
        location.reload();
    })
    .catch(function (error) {
        console.log('Failed while cleaning environment: ' + JSON.stringify(error))
        //odblokuj ekran
        //napisz message
        //przeladuj strone
    })
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function await_result(experiment_run_uid) {
    var state = "initializing";
    while(state != "completed" && state != "error" && state != "canceled") {
        response = await get_transfer_status(experiment_run_uid);
        state = response.state;
        await sleep(2000);
    }
}

var transfer_op_error = function(error) {
    error = error.responseText;
    $("#runButton").prop("disabled", false);
    $("#iterationsSlider").prop("disabled", false);
    enable_divs("#styleImage", "droparea", dropHandlerSet)
    enable_divs("#baseImage", "droparea", dropHandlerSet)
    var errorMsg = 'Failed while transfering style: ' + JSON.stringify(error);
    $("#resultImage").attr("style", "display: none");
    $("#resultErrors").attr("style", "display: block");
    $("#resultErrors").html(errorMsg);
    throw errorMsg;
}

var transfer_style_clicked = function(evt){
    socket.emit("create_connection", socketIOSessionUid)
    iterations = parseInt($("#iterations").html());

    if(iterations < 1) {
        $("#resultErrors").attr("style", "display: block");
        $("#resultErrors").html("Number of iterations should be positive.")
        return
    }

    $("#resultErrors").attr("style", "display: none");
    $("#runButton").prop("disabled", true);
    $("#iterationsSlider").prop("disabled", true);
    disable_divs("#styleImage", "droparea dropareaDisabled")
    disable_divs("#baseImage", "droparea dropareaDisabled")

    $("#resultImage").html(
        "<br />\n" +
        "<div class=\"centeredDiv\">\n" +
        "<img src=\"/staticImages/loading_spinner.gif\" style=\"width: 60px; padding-right: 10px\" /><span id=\"progressMessage\" style=\"color: gray\">Initializing...</span>\n" +
        "</div>"
    )

    transfer_style(styleImage, baseImage, iterations)
    .then(function (data) {
        console.log('Successfully initialized style transfer.')
        console.log('Definition uid: ' + data.definition_uid)
        console.log('Experiment uid: ' + data.experiment_uid)
        console.log('Experiment run uid: ' + data.experiment_run_uid)

        resultImage = data.result_image_id;
        definition_uid = data.definition_uid;
        experimentId = data.experiment_uid;
        runId = data.training_run_uid;

        await_result(data.experiment_run_uid).then(function() {
            $("#runButton").prop("disabled", false);
            $("#iterationsSlider").prop("disabled", false);
            enable_divs("#styleImage", "droparea", dropHandlerSet)
            enable_divs("#baseImage", "droparea", dropHandlerSet)

            url = encodeURI("/images/" + resultImage + "?type=results&prefix=" + runId + "/transfered_images/")

            $("#resultImage").html(
                "<div class=\"grayArea\">" +
                "<div class=\"centeredDiv\">\n" +
                "<img src=\"" + url +  "\" class=\"bottomSpaced resultImage\" />\n" +
                "</div>\n" +
                "<br />\n" +
                "<div class=\"centeredDiv\">\n" +
                "<button id=\"downloadImage\" type=\"button\" class=\"btn btn-default btn-lg bottomSpaced\" type=\"submit\" onclick=\"window.open('" + url + "')\">Download image</button>\n" +
                //"<button id=\"cleanEnv\" type=\"button\" class=\"btn btn-default btn-lg bottomSpaced\">Clean environment</button>\n" +
                "</div>" +
                "</div>"
            )

            $("#cleanEnv").click(clean_env_clicked)
        }).catch(function(error) {
            transfer_op_error(error)
        })
    }).catch(function (error) {
        transfer_op_error(error)
    });
}

$("#runButton").prop("disabled", true);
$("#runButton").click(transfer_style_clicked)