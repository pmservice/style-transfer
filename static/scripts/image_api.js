var send_image = function(file) {
    var formData = new FormData();
    formData.append("image_file", file);

    var req = {
        url: "/images",
        method: "post",
        processData: false,
        contentType: false,
        data: formData
    };

    return $.ajax(req);
}

var get_transfer_status = function(experiment_run_uid) {
    var req = {
        url: "/images/transferStyle/" + experiment_run_uid,
        method: "get",
        processData: false,
        contentType: false
    };

    return $.ajax(req);
}

var transfer_style = function(styleImage, baseImage, iteration=1) {
    var req = {
        url: "/images/transferStyle?styleImage="+styleImage+"&baseImage="+baseImage+"&iteration=" + iteration,
        method: "post",
        processData: false,
        contentType: false
    };

    return $.ajax(req);
}

var clean_env = function(styleImage, baseImage, resultImage, definition_url, experimentId, runId) {
    var req = {
        url: "/cleanEnv?style_image=" + styleImage +
            "&base_image=" + baseImage +
            "&result_image=" + resultImage +
            "&definition_uid=" + definition_url +
            "&experiment_uid=" + experimentId +
            "&experiment_run_uid=" + runId,
        method: "post",
        processData: false,
        contentType: false
    };

    return $.ajax(req);
}