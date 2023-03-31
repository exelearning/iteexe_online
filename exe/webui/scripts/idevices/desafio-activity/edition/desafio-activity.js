/**
 * Challenge iDevice (edition code)
 * Released under Attribution-ShareAlike 4.0 International License.
 * Author: Manuel Narváez Martínez
 * Graphic design: Ana María Zamora Moreno, Francisco Javier Pulido
 * Testers: Ricardo Málaga Floriano, Francisco Muñoz de la Peña
 * Translator: Antonio Juan Delgado García
 * License: http://creativecommons.org/licenses/by-sa/4.0/
 */
var $exeDevice = {
    // i18n
    i18n: {
        name: _('Challenge'),
    },
    iDevicePath: "/scripts/idevices/desafio-activity/edition/",
    msgs: {},
    active: 0,
    numberId: 0,
    typeActive: 0,
    challengesGame: [],
    desafioTitle: '',
    desafioTime: 40,
    desafioSolution: '',
    desafioDescription: '',
    typeEdit: -1,
    numberCutCuestion: -1,
    desafioFeedBacks: [],
    desafioVersion: 1,
    clipBoard: '',
    desafioID: 0,
    ci18n: {
        "msgStartGame": _("Click here to start"),
        "msgSubmit": _("Submit"),
        "msgInformationLooking": _("Cool! The information you were looking for"),
        "msgPlayStart": _("Click here to play"),
        "msgMinimize": _("Minimize"),
        "msgMaximize": _("Maximize"),
        "msgTime": _("Time per question"),
        "msgNoImage": _("No picture question"),
        "msgSuccesses": _("Right! | Excellent! | Great! | Very good! | Perfect!"),
        "msgFailures": _("It was not that! | Incorrect! | Not correct! | Sorry! | Error!"),
        "msgInformation": _("Information"),
        "mgsSolution": _("Solution"),
        "msgDate": _("Date"),
        "msgDesafio": _("Challenge"), // Desafío in ES
        "msgChallenge": _("Trial"), // Reto in ES
        "msgChallengesCompleted": _("Completed trials"),
        "msgStartTime": _("Starting time"),
        "msgReadTime": _("Read the instructions and click on a trial when you're ready to play."),
        "msgChallengesAllCompleted": _("You've completed all the trials! You can now complete the game."),
        "msgDesafioSolved": _("You made it! You can restart to play again."),
        "msgDesafioSolved1": _("You solved the trial! Congratulations!"),
        "msgEndTime": _("Time Over. Please restart to try again."),
        "msgSolutionError": _("Sorry. Wrong solution."),
        "msgSolutionCError": _("Sorry. The solution is wrong."),
        "msgChallengeSolved": _("You solved this trial! Please select another one."),
        "msgDesafioReboot": _("Restart the game and the starting time?"),
        "msgCompleteAllChallenged": _("You must complete all the trials to finish."),
        "msgSolvedChallenge": _("You already completed this trial."),
        "msgWriteChallenge": _("Complete the trial. Write the solution."),
        "msgEndTimeRestart": _("Time Over. Please restart to try again."),
        "msgReboot": _("Restart"),
        "msgHelp": _("Help"),
        "msgScoreScorm": _("The score can't be saved because this page is not part of a SCORM package."),
        "msgEndGameScore": _("Please start the game before saving your score."),
        "msgOnlySaveScore": _("You can only save the score once!"),
        "msgOnlySave": _("You can only save once"),
        "msgInformation": _("Information"),
        "msgYouScore": _("Your score"),
        "msgAuthor": _("Authorship"),
        "msgOnlySaveAuto": _("Your score will be saved after each question. You can only play once."),
        "msgSaveAuto": _("Your score will be automatically saved after each question."),
        "msgSeveralScore": _("You can save the score as many times as you want"),
        "msgYouLastScore": _("The last score saved is"),
        "msgActityComply": _("You have already done this activity."),
        "msgPlaySeveralTimes": _("You can do this activity as many times as you want")

    },
    getId: function () {
        return Math.round(new Date().getTime() + (Math.random() * 100));
    },
    init: function () {
        this.desafioID = this.getId();
        this.setMessagesInfo();
        this.createForm();
        

    },
    setMessagesInfo: function () {
        var msgs = this.msgs;
        msgs.msgESelectFile = _("The selected file does not contain a valid game");
        msgs.msgTitleDesafio = _("Please write the challenge title.");
        msgs.msgDescriptionDesafio = _("Please write the challenge description.");
        msgs.msgSolutionDesafio = _("Please write the challenge solution.");
        msgs.msgOneChallenge = _("Please add at least one trial.");
        msgs.msgTenChallenges = _("You can only add ten trials.");
        msgs.msgDataChanllenge = _("Please write the title, description and solution of all the trials.");
        msgs.msgNoSuportBrowser = _("Your browser is not compatible with this tool.");
        msgs.msgClue = _("Help");
    },
    showMessage: function (msg) {
        eXe.app.alert(msg);
    },
    addChallenge: function () {
        $exeDevice.saveChallenge();
        if ($exeDevice.challengesGame.length == 10) {
            $exeDevice.showMessage($exeDevice.msgs.msgTenChallenges);
            return;
        }
        $exeDevice.typeEdit = -1;
        $exeDevice.numberId++;
        $exeDevice.clearChallenge();
        $exeDevice.challengesGame.push($exeDevice.getChallengeDefault());
        $exeDevice.active = $exeDevice.challengesGame.length - 1;
        $('#desafioENumberChallenge').text($exeDevice.active + 1);
        $('#desafioEPaste').hide();
        $('#desafioENumChallenges').text($exeDevice.challengesGame.length);
        $('.desafio-EDivFeebBack').hide();
        $('#desafioEDivFeebBack-' + $exeDevice.active).show();
        if (tinyMCE.get('desafioEChallenge-' + $exeDevice.active)) {
            tinyMCE.get('desafioEChallenge-' + $exeDevice.active).setContent('');
        } else {
            $('desafioEChallenge-' + $exeDevice.active).val('');
        }
    },
    clearChallenge: function () {
        $('#desafioECTitle').val('');
        $('#desafioECSolution').val('');
        $('#desafioECMessage').val('');
        $('#desafioECTime').val(5);

    },
    removeChallenge: function () {
        if ($exeDevice.challengesGame.length < 2) {
            $exeDevice.showMessage($exeDevice.msgs.msgOneChallenge);
            return;
        } else {
            $exeDevice.challengesGame.splice($exeDevice.active, 1);
            if ($exeDevice.active >= $exeDevice.challengesGame.length - 1) {
                $exeDevice.active = $exeDevice.challengesGame.length - 1;
            }
            $exeDevice.typeEdit = -1;
            $('#desafioEPaste').hide();
            $('#desafioENumChallenges').text($exeDevice.challengesGame.length);
            $('#desafioENumberChallenge').text($exeDevice.active + 1);
            $exeDevice.updateFeedBack();
            $exeDevice.showChallenge($exeDevice.active);
        }

    },
    updateFeedBack: function () {
        for (var i = 0; i < 10; i++) {
            var text = '';
            if (i < $exeDevice.challengesGame.length) {
                text = $exeDevice.challengesGame[i].description
            }
            if (tinyMCE.get('desafioEChallenge-' + i)) {
                tinyMCE.get('desafioEChallenge-' + i).setContent(text);
            } else {
                $('desafioEChallenge-' + i).val(text);
            }
        }
    },
    copyChallenge: function () {
        $exeDevice.saveChallenge();
        $exeDevice.typeEdit = 0;
        $exeDevice.clipBoard = $exeDevice.challengesGame[$exeDevice.active];
        $('#desafioEPaste').show();

    },
    cutChallenge: function () {
        $exeDevice.saveChallenge();
        $exeDevice.numberCutCuestion = $exeDevice.active;
        $exeDevice.typeEdit = 1;
        $('#desafioEPaste').show();
    },
    arrayMove: function (arr, oldIndex, newIndex) {
        if (newIndex >= arr.length) {
            var k = newIndex - arr.length + 1;
            while (k--) {
                arr.push(undefined);
            }
        }
        arr.splice(newIndex, 0, arr.splice(oldIndex, 1)[0]);
    },

    pasteChallenge: function () {
        if ($exeDevice.challengesGame.length > (9 + $exeDevice.typeEdit)) {
            $('#desafioEPaste').hide();
            $exeDevice.showMessage($exeDevice.msgs.msgTenChallenges);
            return;
        }
        if ($exeDevice.typeEdit == 0) {
            $exeDevice.active++;
            $exeDevice.challengesGame.splice($exeDevice.active, 0, $exeDevice.clipBoard);
            $exeDevice.updateFeedBack();
            $exeDevice.showChallenge($exeDevice.active);
        } else if ($exeDevice.typeEdit == 1) {
            $('#desafioEPaste').hide();
            $exeDevice.typeEdit = -1;
            $exeDevice.arrayMove($exeDevice.challengesGame, $exeDevice.numberCutCuestion, $exeDevice.active);
            $exeDevice.updateFeedBack();
            $exeDevice.showChallenge($exeDevice.active);
            $('#desafioENumChallenges').text($exeDevice.challengesGame.length);
        }

    },
    nextChallenge: function () {
        $exeDevice.saveChallenge();
        if ($exeDevice.active < $exeDevice.challengesGame.length - 1) {
            $exeDevice.active++;
            $exeDevice.showChallenge($exeDevice.active);
        }
    },
    lastChallenge: function () {
        $exeDevice.saveChallenge();
        if ($exeDevice.active < $exeDevice.challengesGame.length - 1) {
            $exeDevice.active = $exeDevice.challengesGame.length - 1;
            $exeDevice.showChallenge($exeDevice.active);
        }
    },
    previousChallenge: function () {
        $exeDevice.saveChallenge();
        if ($exeDevice.active > 0) {
            $exeDevice.active--;
            $exeDevice.showChallenge($exeDevice.active);
        }
    },
    firstChallenge: function () {
        $exeDevice.saveChallenge();
        if ($exeDevice.active > 0) {
            $exeDevice.active = 0;
            $exeDevice.showChallenge($exeDevice.active);
        }
    },
    showChallenge: function (i) {
        var num = i < 0 ? 0 : i;
        num = num >= $exeDevice.challengesGame.length ? $exeDevice.challengesGame.length - 1 : num;
        $('#desafioENumQuestionDiv').show();
        $('#desafiolblEDTime').hide();
        $('#desafioEDTime').hide();
        $('#desafiolblEDType').hide();
        $('#desafioEDType').hide();
        $('label[for=desafioEDSolution], #desafioEDSolution').hide();
        $('label[for=desafioEDTitle], #desafioEDTitle').hide();
        $('label[for=desafioECTitle], #desafioECTitle').show();
        $('label[for=desafioECSolution], #desafioECSolution').show();
        $('#desafioENavigationButtons').show();
        var c = $exeDevice.challengesGame[num];
        $('#desafioECTitle').val(c.title);
        $('#desafioECSolution').val(c.solution);
        $('#divDesafioEDescription').hide();
        $('.desafio-EDivFeebBack').hide();
        $('#desafioEDivFeebBack-' + i).show();
        $('#desafioEChallenges').show();
        $('#desafioENumChallenges').text($exeDevice.challengesGame.length);
        $('#desafioENumberChallenge').text($exeDevice.active + 1);
        if (typeof c.clues != "undefined") {
            $('#desafioEClue1').val(c.clues[0].clue);
            $('#desafioEClue2').val(c.clues[1].clue);
            $('#desafioEClue3').val(c.clues[2].clue);
            $('#desafioECTime1').val(c.clues[0].time);
            $('#desafioECTime2').val(c.clues[1].time);
            $('#desafioECTime3').val(c.clues[2].time)
        }

    },

    createForm: function () {
        var path = $exeDevice.iDevicePath,
            html = '\
			<div id="desafioIdeviceForm">\
                <div class="exe-idevice-info">'+_("Create escape room type activities in which players will have to complete trials before solving the final challenge.")+' <a href="https://youtu.be/KqfqoarVGro" hreflang="es" rel="lightbox"  target="_blank">'+_("Use Instructions")+'</a></div>\
				<div class="exe-form-tab" title="' + _('General settings') + '">\
                ' + $exeAuthoring.iDevice.gamification.instructions.getFieldset(_("Complete all the trials to finish the activity.")) + '\
                    <fieldset class="exe-fieldset exe-fieldset-closed">\
                        <legend><a href="#">' + _("Options") + '</a></legend>\
                        <div>\
                            <p>\
                                <label for="desafioEShowMinimize"><input type="checkbox" id="desafioEShowMinimize">' + _("Show minimized.") + '</label>\
                            </p>\
                        </div>\
                    </fieldset>\
                    <fieldset class="exe-fieldset">\
                        <legend><a href="#">' + _("Questions") + '</a></legend>\
                        <div class="desafio-EPanel" id="desafioEPanel">\
                            <div class="desafioToggle">\
                                    <input class="desafio-Type" checked="checked" id="desafioEDesafio" type="radio" name="dsfDesRet" value="0" />\
                                    <label for="desafioEDesafio">' + _("Challenge") + '</label>\
                                    <input class="desafio-Type"  id="desafioEReto" type="radio" name="dsfDesRet" value="1" />\
                                    <label for="desafioEReto">' + _("Trials") + '</label>\
                            </div>\
                            <div class="desafio-EDAtaGame">\
                                <div class="desafio-EDataChallenger">\
                                    <p class="desafio-DataDesafio">\
                                        <label for="desafioEDTitle">' + _("Title") + ':</label><input type="text" id="desafioEDTitle" />\
                                        <label for="desafioEDSolution">' + _("Solution") + ':</label><input type="text" id="desafioEDSolution" />\
                                        <label for="desafioECTitle">' + _("Title") + ':</label><input type="text" id="desafioECTitle" />\
                                        <label for="desafioECSolution">' + _("Solution") + ':</label><input type="text" id="desafioECSolution" />\
                                    </p>\
                                    <p>\
                                        <label id="desafiolblEDType" for="desafioEDType">' + _("Type") + ': </label>\
                                        <select id="desafioEDType">\
                                            <option value="0">Lineal</option>\
                                            <option value="1">Libre</option>\
                                        </select>\
                                        <label id="desafiolblEDTime" for="desafioEDTime" >' + _("Max time") + ': </label>\
                                        <select id="desafioEDTime">\
                                            <option value="1">1m</option>\
                                            <option value="10">10m</option>\
                                            <option value="15">15m</option>\
                                            <option value="20">20m</option>\
                                            <option value="25">25m</option>\
                                            <option value="30">30m</option>\
                                            <option value="35">35m</option>\
                                            <option value="40" selected>40m</option>\
                                            <option value="40">45m</option>\
                                            <option value="50">50m</option>\
                                            <option value="55">55m</option>\
                                            <option value="60">60m</option>\
                                            <option value="70">70m</option>\
                                            <option value="80">80m</option>\
                                            <option value="90">90m</option>\
                                            <option value="120">120m</option>\
                                            <option value="150">150</option>\
                                            <option value="180">180m</option>\
                                            <option value="210">210m</option>\
                                            <option value="240">240m</option>\
                                        </select>\
                                     </p>\
                                </div>\
                                <div class="desafio-EInputMedias">\
                                    <span>' + _("Description") + ':</span>\
                                    <div id="divDesafioEDescription">\
                                        <label for="desafioEDescription" class="sr-av">' + _('Instructions') + '":</label>\
                                        <textarea id="desafioEDescription" class="exe-html-editor"\></textarea>\
                                    </div>\
                                    <div id="desafioEChallenges">\
                                    ' + this.getDivChallenges(10) + '\
                                    </div>\
                                    <div class="desafio-EClues" id="desafioEClues">\
                                    ' + this.getDivClues() + '\
                                    </div>\
                                </div>\
                            </div>\
                            <div class="desafio-ENavigationButtons" id="desafioENavigationButtons">\
                                <a href="#" id="desafioEAdd" class="desafio-ENavigationButton" title="' + _("Add question") + '"><img src="' + path + 'quextIEAdd.png" alt="' + _("Add question") + '" class="desafio-EButtonImage b-add" /></a>\
                                <a href="#" id="desafioEFirst" class="desafio-ENavigationButton"  title="' + _("First question") + '"><img src="' + path + 'quextIEFirst.png" alt="' + _("First question") + '" class="desafio-EButtonImage b-first" /></a>\
                                <a href="#" id="desafioEPrevious" class="desafio-ENavigationButton" title="' + _("Previous question") + '"><img src="' + path + 'quextIEPrev.png" alt="' + _("Previous question") + '" class="desafio-EButtonImage b-prev" /></a>\
                                <span class="sr-av">' + _("Question number:") + '</span><span class="desafio-NumberQuestion" id="desafioENumberChallenge">1</span>\
                                <a href="#" id="desafioENext" class="desafio-ENavigationButton"  title="' + _("Next question") + '"><img src="' + path + 'quextIENext.png" alt="' + _("Next question") + '" class="desafio-EButtonImage b-next" /></a>\
                                <a href="#" id="desafioELast" class="desafio-ENavigationButton"  title="' + _("Last question") + '"><img src="' + path + 'quextIELast.png"  alt="' + _("Last question") + '" class="desafio-EButtonImage b-last" /></a>\
                                <a href="#" id="desafioEDelete" class="desafio-ENavigationButton" title="' + _("Delete question") + '"><img src="' + path + 'quextIEDelete.png" alt="' + _("Delete question") + '" class="desafio-EButtonImage b-delete" /></a>\
                                <a href="#" id="desafioECopy" class="desafio-ENavigationButton" title="' + _("Copy question") + '"><img src="' + path + 'quextIECopy.png"  alt="' + _("Copy question") + '" class="desafio-EButtonImage b-copy" /></a>\
                                <a href="#" id="desafioECut" class="desafio-ENavigationButton" title="' + _("Cut question") + '"><img src="' + path + 'quextIECut.png"  alt="' + _("Cut question") + '"  class="desafio-EButtonImage b-cut" /></a>\
                                <a href="#" id="desafioEPaste" class="desafio-ENavigationButton"  title="' + _("Paste question") + '"><img src="' + path + 'quextIEPaste.png"  alt="' + _("Paste question") + '" class="desafio-EButtonImage b-paste" /></a>\
                            </div>\
                            <div class="desafio-ENumQuestionDiv" id="desafioENumQuestionDiv">\
                               <div class="desafio-ENumQ"><span class="sr-av">' + _("Number of questions:") + '</span></div>\
                               <span class="desafio-ENumQuestions" id="desafioENumChallenges">0</span>\
                            </div>\
                        </div>\
                    </fieldset>\
                </div>\
    			' + $exeAuthoring.iDevice.gamification.common.getLanguageTab(this.ci18n) + '\
                ' + $exeAuthoring.iDevice.gamification.scorm.getTab() + '\
		    </div>\
			';
        var field = $("textarea.jsContentEditor").eq(0)
        field.before(html);
        $exeAuthoring.iDevice.tabs.init("desafioIdeviceForm");
        $exeAuthoring.iDevice.gamification.scorm.init();

        $exeDevice.loadPreviousValues(field);
        $exeDevice.addEvents();
        $exeDevice.showDesafio();

    },
    getDivChallenges: function (num) {
        var chs = '';
        for (var j = 0; j < num; j++) {
            var ch = '<div class="desafio-EDivFeebBack" id="desafioEDivFeebBack-' + j + '">\
            <label for="desafioEChallenge-' + j + '" class="sr-av">' + _('Feedback') + '":</label>\
            <textarea id="desafioEChallenge-' + j + '" class="exe-html-editor desafio-EFeedBack"\></textarea>\
            </div>'
            chs += ch;
        }
        return chs;
    },
    getDivClues: function () {
        var chs = ' <p class="desafio-EClue">\
        <label for="desafioEClue1">' + _("Help") + ' 1:</label><input type="text" id="desafioEClue1" />\
        <label id="desafiolblECTime1" for="desafioECTime1" class="sr-av">' + _("Time") + ':</label>\
        <select id="desafioECTime1">\
            <option value="1">1m</option>\
            <option value="3">3m</option>\
            <option value="5" selected>5m</option>\
            <option value="10">10m</option>\
            <option value="15">15m</option>\
            <option value="20" >20m</option>\
            <option value="25">25m</option>\
            <option value="30">30m</option>\
            <option value="35">35m</option>\
            <option value="40">40m</option>\
            <option value="45">45m</option>\
            <option value="50">50m</option>\
            <option value="55">55m</option>\
            <option value="60">60m</option>\
            <option value="65">65m</option>\
            <option value="70">70m</option>\
            <option value="75">75m</option>\
            <option value="80">80m</option>\
            <option value="85">55m</option>\
            <option value="90">90m</option>\
            <option value="95">75m</option>\
            <option value="100">100m</option>\
            <option value="110">110m</option>\
            <option value="120">120m</option>\
            <option value="150">150</option>\
            <option value="180">180m</option>\
            <option value="210">210m</option>\
            <option value="240">240m</option>\
        </select>\
    </p>\
    <p class="desafio-EClue">\
        <label for="desafioEClue2">' + _("Help") + ' 2:</label><input type="text"  id="desafioEClue2" />\
        <label id="desafiolblECTime2" for="desafioECTime2" class="sr-av">' + _("Time") + ' :</label>\
            <select id="desafioECTime2">\
            <option value="1">1m</option>\
            <option value="3">3m</option>\
            <option value="5">5m</option>\
            <option value="10" selected>10m</option>\
            <option value="15">15m</option>\
            <option value="20">20m</option>\
            <option value="25">25m</option>\
            <option value="30">30m</option>\
            <option value="35">35m</option>\
            <option value="40">40m</option>\
            <option value="45">45m</option>\
            <option value="50">50m</option>\
            <option value="55">55m</option>\
            <option value="60">60m</option>\
            <option value="65">65m</option>\
            <option value="70">70m</option>\
            <option value="75">75m</option>\
            <option value="80">80m</option>\
            <option value="85">55m</option>\
            <option value="90">90m</option>\
            <option value="95">75m</option>\
            <option value="100">100m</option>\
            <option value="110">110m</option>\
            <option value="120">120m</option>\
            <option value="150">150</option>\
            <option value="180">180m</option>\
            <option value="210">210m</option>\
            <option value="240">240m</option>\
        </select>\
    </p>\
    <p class="desafio-EClue">\
        <label for="desafioEClue3">' + _("Help") + ' 3:</label><input type="text"  id="desafioEClue3" />\
        <label id="desafiolblECTime3" for="desafioECTime3" class="sr-av">' + _("Time") + ':</label>\
        <select id="desafioECTime3">\
        <option value="1">1m</option>\
        <option value="3">3m</option>\
        <option value="5">5m</option>\
        <option value="10">10m</option>\
        <option value="15" selected>15m</option>\
        <option value="20">20m</option>\
        <option value="25">25m</option>\
        <option value="30">30m</option>\
        <option value="35">35m</option>\
        <option value="40">40m</option>\
        <option value="45">45m</option>\
        <option value="50">50m</option>\
        <option value="55">55m</option>\
        <option value="60">60m</option>\
        <option value="65">65m</option>\
        <option value="70">70m</option>\
        <option value="75">75m</option>\
        <option value="80">80m</option>\
        <option value="85">55m</option>\
        <option value="90">90m</option>\
        <option value="95">75m</option>\
        <option value="100">100m</option>\
        <option value="119">110m</option>\
        <option value="120">120m</option>\
        <option value="150">150</option>\
        <option value="180">180m</option>\
        <option value="210">210m</option>\
        <option value="240">240m</option>\
        </select>\
    </p>';
        return chs;
    },
    getChallengeDefault: function () {
        var p = new Object();
        p.title = '';
        p.solution = '';
        p.description = '';
        return p;
    },
    loadPreviousValues: function (field) {
        var originalHTML = field.val();
        if (originalHTML != '') {
            $exeDevice.active = 0;
            var wrapper = $("<div></div>");
            wrapper.html(originalHTML);
            var json = $('.desafio-DataGame', wrapper).text(),
                version = $('.desafio-version', wrapper).text();
            if (version.length == 1 || !json.startsWith('{')) {
                json = $exeDevice.Decrypt(json);
            }
            var dataGame = $exeDevice.isJsonString(json);
            $exeDevice.desafioTitle = dataGame.desafioTitle;
            $exeDevice.active = 0;
            $exeDevice.desafioSolution = dataGame.desafioSolution;
            $exeDevice.desafioType = dataGame.desafioType;
            $exeDevice.desafioTime = dataGame.desafioTime;
            $exeDevice.desafioDescription = $('.desafio-EDescription', wrapper).html();
            if (tinyMCE.get('desafioEDescription')) {
                tinyMCE.get('desafioEDescription').setContent();
            } else {
                $('#desafioEDescription').val($('.desafio-EDescription', wrapper).html());
            }
            $('.desafio-ChallengeDescription', wrapper).each(function (i) {
                dataGame.challengesGame[i].description = $(this).html();
                if (tinyMCE.get('desafioEChallenge-' + i)) {
                    tinyMCE.get('desafioEChallenge-' + i).setContent($(this).html());
                } else {
                    $('#desafioEChallenge-' + i).val($(this).html());
                }
            });
            $exeDevice.challengesGame = dataGame.challengesGame;
            var c = $exeDevice.challengesGame[0];
            $('#desafioECTitle').val(c.title);
            $('#desafioECSolution').val(c.solution);
            if (typeof c.clues != "undefined") {
                $('#desafioEClue1').val(c.clues[0].clue);
                $('#desafioEClue2').val(c.clues[1].clue);
                $('#desafioEClue3').val(c.clues[2].clue);
                $('#desafioECTime1').val(c.clues[0].time);
                $('#desafioECTime2').val(c.clues[1].time);
                $('#desafioECTime3').val(c.clues[2].time)
            }
            var instructions = $(".desafio-instructions", wrapper);
            if (instructions.length == 1) $("#eXeGameInstructions").val(instructions.html());
            $exeAuthoring.iDevice.gamification.common.setLanguageTabValues(dataGame.msgs);
            $exeDevice.updateFieldGame(dataGame);
        }
    },
    Encrypt: function (str) {
        if (!str) str = "";
        str = (str == "undefined" || str == "null") ? "" : str;
        try {
            var key = 146;
            var pos = 0;
            var ostr = '';
            while (pos < str.length) {
                ostr = ostr + String.fromCharCode(str.charCodeAt(pos) ^ key);
                pos += 1;
            }
            return escape(ostr);
        } catch (ex) {
            return '';
        }
    },

    Decrypt: function (str) {
        if (!str) str = "";
        str = (str == "undefined" || str == "null") ? "" : str;
        str = unescape(str)
        try {
            var key = 146;
            var pos = 0;
            var ostr = '';
            while (pos < str.length) {
                ostr = ostr + String.fromCharCode(key ^ str.charCodeAt(pos));
                pos += 1;
            }

            return ostr;
        } catch (ex) {
            return '';
        }
    },
    updateFieldGame: function (game) {
        $('#desafioEShowMinimize').prop('checked', game.showMinimize);
        $exeDevice.desafioID = typeof game.desafioID == "undefined" ? $exeDevice.desafioID : game.desafioID;
        $exeAuthoring.iDevice.gamification.scorm.setValues(game.isScorm, game.textButtonScorm, game.repeatActivity);
        $exeDevice.showDesafio();

    },
    isJsonString: function (str) {
        try {
            var o = JSON.parse(str, null, 2);
            if (o && typeof o === "object") {
                return o;
            }
        } catch (e) {}
        return false;
    },

    save: function () {
        var dataGame = this.validateData();
        if (!dataGame) {
            return false;
        }
        var fields = this.ci18n,
            i18n = fields;
        for (var i in fields) {
            var fVal = $("#ci18n_" + i).val();
            if (fVal != "") i18n[i] = fVal;
        }
        dataGame.msgs = i18n;
        var json = JSON.stringify(dataGame),
            divContent = "";
        json = $exeDevice.Encrypt(json);
        var instructions = tinyMCE.get('eXeGameInstructions').getContent(),
            description = tinyMCE.get('desafioEDescription').getContent();
        if (instructions != "") divContent = '<div class="desafio-instructions">' + instructions + '</div>';
        var html = '<div class="desafio-IDevice">';
        html += divContent;
        html += '<div class="desafio-version js-hidden">' + $exeDevice.desafioVersion + '</div>';
        html += '<div class="desafio-EDescription">' + description + '</div>';
        for (var i = 0; i < $exeDevice.challengesGame.length; i++) {
            var df = tinyMCE.get('desafioEChallenge-' + i).getContent();
            html += '<div class="desafio-ChallengeDescription">' + df + '</div>';
        }
        html += '<div class="desafio-DataGame js-hidden">' + json + '</div>';
        html += '<div class="desafio-bns js-hidden">' + $exeDevice.msgs.msgNoSuportBrowser + '</div>';
        html += '</div>';
        return html;
    },

    saveChallenge: function () {
        var message = '',
            p = new Object(),
            i = $exeDevice.active;
        if (tinyMCE.get('desafioEChallenge-' + i)) {
            p.description = tinyMCE.get('desafioEChallenge-' + i).getContent();
        } else {
            p.description = $('desafioEChallenge-' + i).val();
        }
        p.title = $('#desafioECTitle').val();
        p.solution = $('#desafioECSolution').val();
        p.timeShow=-1;
        var clues = [{
            "clue": $('#desafioEClue1').val(),
            "time": parseInt($('#desafioECTime1 option:selected').val()),

        },
        {
            "clue": $('#desafioEClue2').val(),
            "time": parseInt($('#desafioECTime2 option:selected').val()),
        },
        {
            "clue": $('#desafioEClue3').val(),
            "time": parseInt($('#desafioECTime3 option:selected').val()),

        }];
        p.clues = clues;
        $exeDevice.challengesGame[i] = p;
        return message;

    },

    saveDesafio: function () {
        $exeDevice.desafioTitle = $('#desafioEDTitle').val();
        $exeDevice.desafioSolution = $('#desafioEDSolution').val();
        $exeDevice.desafioType = parseInt($('#desafioEDType option:selected').val());
        $exeDevice.desafioTime = parseInt($('#desafioEDTime option:selected').val());
        $exeDevice.desafioDescription = "";
        if (tinyMCE.get('desafioEDescription')) {
            $exeDevice.desafioDescription = tinyMCE.get('desafioEDescription').getContent();
        } else {
            $exeDevice.desafioDescription = $('#desafioEDescription').val();
        }
    },

    exportGame: function () {

        var dataGame = this.validateData();
        if (!dataGame) {
            return false;
        }
        var blob = JSON.stringify(dataGame),
            newBlob = new Blob([blob], {
                type: "text/plain"
            });
        if (window.navigator && window.navigator.msSaveOrOpenBlob) {
            window.navigator.msSaveOrOpenBlob(newBlob);
            return;
        }
        const data = window.URL.createObjectURL(newBlob);
        var link = document.createElement('a');
        link.href = data;
        link.download = _("Game") + "desafio.json";
        document.getElementById('desafioIdeviceForm').appendChild(link);
        link.click();
        setTimeout(function () {
            document.getElementById('desafioIdeviceForm').removeChild(link);
            window.URL.revokeObjectURL(data);
        }, 100);
    },
    importGame: function (content) {
        var game = $exeDevice.isJsonString(content);
        if (!game || typeof game.typeGame == "undefined") {
            $exeDevice.showMessage($exeDevice.msgs.msgESelectFile);
            return;
        } else if (game.typeGame !== 'desafio') {
            $exeDevice.showMessage($exeDevice.msgs.msgESelectFile);
            return;
        }
        $exeDevice.active = 0;
        $exeDevice.desafioTitle = game.desafioTitle;
        $exeDevice.desafioSolution = game.desafioSolution;
        $exeDevice.desafioDescription = (game.desafioDescription);
        $exeDevice.desafioType = game.desafioType;
        $exeDevice.desafioTime = game.desafioTime;
        for (var i = 0; i < $exeDevice.challengesGame.length; i++) {
            game.challengesGame[i].description = (game.challengesGame[i].description);
        }
        $exeDevice.challengesGame = game.challengesGame;
        $exeDevice.updateFieldGame(game);
        var instructions = game.instructionsExe || game.instructions;
        tinymce.editors[0].setContent((instructions));
        $('.exe-form-tabs li:first-child a').click();
    },
    validateData: function () {
        $exeDevice.saveDesafio();
        $exeDevice.saveChallenge();
        var instructions = $('#eXeGameInstructions').text(),
            instructionsExe = (tinyMCE.get('eXeGameInstructions').getContent()),
            showMinimize = $('#desafioEShowMinimize').is(':checked');
        if ($exeDevice.desafioTitle.length == 0) {
            $exeDevice.showMessage($exeDevice.msgs.msgTitleDesafio);
            return false;
        } else if ($exeDevice.desafioSolution.length == 0) {
            $exeDevice.showMessage($exeDevice.msgs.msgSolutionDesafio);
            return false;
        } else if ($exeDevice.desafioDescription == 0) {
            $exeDevice.showMessage($exeDevice.msgs.msgDescriptionDesafio);
            return false;
        }
        var challengesGame = $exeDevice.challengesGame;
        for (var i = 0; i < challengesGame.length; i++) {
            var mChallenge = challengesGame[i]
            if (mChallenge.title.length == 0 || mChallenge.solution.length == 0 || mChallenge.description.length == 0) {
                $exeDevice.showMessage($exeDevice.msgs.msgDataChanllenge);
                return false;
            }
        }
        var scorm = $exeAuthoring.iDevice.gamification.scorm.getValues();
        var data = {
            'asignatura': '',
            "author": '',
            'typeGame': 'desafio',
            'desafioTitle': $exeDevice.desafioTitle,
            'desafioTime': $exeDevice.desafioTime,
            'desafioType': $exeDevice.desafioType,
            'desafioSolution': $exeDevice.desafioSolution,
            'desafioSolved': false,
            'desafioDescription': $exeDevice.desafioDescription,
            'instructionsExe': instructionsExe,
            'instructions': instructions,
            'showMinimize': showMinimize,
            'challengesGame': challengesGame,
            'title': '',
            'isScorm': scorm.isScorm,
            'textButtonScorm': scorm.textButtonScorm,
            'repeatActivity': scorm.repeatActivity,
            'desafioID': $exeDevice.desafioID,
        }
        return data;
    },
    removeTags: function (str) {
        var wrapper = $("<div></div>");
        wrapper.html(str);
        return wrapper.text();
    },
    addEvents: function () {
        if ($exeDevice.challengesGame.length == 0) {
            var challenge = $exeDevice.getChallengeDefault();
            $exeDevice.active = 0,
                $exeDevice.challengesGame.push(challenge);
        }
        $('#desafioENavigationButtons').hide();
        $('#desafioEPaste').hide();
        $('#desafioENumQuestionDiv').hide();
        $('#desafioEUseLives').on('change', function () {
            var marcado = $(this).is(':checked');
            $('#desafioENumberLives').prop('disabled', !marcado);
        });
        $('#desafioShowSolutions').on('change', function () {
            var marcado = $(this).is(':checked');
            $('#desafioTimeShowSolutions').prop('disabled', !marcado);
        });

        $('#desafioShowCodeAccess').on('change', function () {
            var marcado = $(this).is(':checked');
            $('#desafioCodeAccess').prop('disabled', !marcado);
            $('#desafioMessageCodeAccess').prop('disabled', !marcado);
        });

        $('#desafioEAdd').on('click', function (e) {
            e.preventDefault();
            $exeDevice.addChallenge()
        });
        $('#desafioEFirst').on('click', function (e) {
            e.preventDefault();
            $exeDevice.firstChallenge()
        });
        $('#desafioEPrevious').on('click', function (e) {
            e.preventDefault();
            $exeDevice.previousChallenge()
        });
        $('#desafioENext').on('click', function (e) {
            e.preventDefault();
            $exeDevice.nextChallenge()
        });
        $('#desafioELast').on('click', function (e) {
            e.preventDefault();
            $exeDevice.lastChallenge()
        });
        $('#desafioEDelete').on('click', function (e) {
            e.preventDefault();
            $exeDevice.removeChallenge()
        });
        $('#desafioECopy').on('click', function (e) {
            e.preventDefault();
            $exeDevice.copyChallenge()
        });
        $('#desafioECut').on('click', function (e) {
            e.preventDefault();
            $exeDevice.cutChallenge()
        });
        $('#desafioEPaste').on('click', function (e) {
            e.preventDefault();
            $exeDevice.pasteChallenge()
        });
        $('#desafioEDesafio').on('click', function (e) {
            if ($exeDevice.typeActive != 0) {
                $exeDevice.typeActive = 0;
                $exeDevice.saveChallenge();
                $exeDevice.showDesafio();
                $exeDevice.showClues(false);
            }

        });
        $('#desafioEReto').on('click', function (e) {
            if ($exeDevice.typeActive != 1) {
                $exeDevice.typeActive = 1;
                $exeDevice.saveDesafio();
                $exeDevice.showChallenge($exeDevice.active);
                $exeDevice.showClues(true);
            }
        });

        if (window.File && window.FileReader && window.FileList && window.Blob) {
            $('#eXeGameExportImport').show();
            $('#eXeGameImportGame').on('change', function (e) {
                var file = e.target.files[0];
                if (!file) {
                    return;
                }
                var reader = new FileReader();
                reader.onload = function (e) {
                    $exeDevice.importGame(e.target.result);
                };
                reader.readAsText(file);
            });
            $('#eXeGameExportGame').on('click', function () {
                $exeDevice.exportGame();
            })
        } else {
            $('#eXeGameExportImport').hide();
        }

    },
    showClues: function (show) {
        if (show) {
            $('#desafioEClues').show();
        } else {
            $('#desafioEClues').hide();
        }

    },

    showDesafio: function () {
        $exeDevice.typeActive = 0;
        $('#desafiolblEDTime').show();
        $('#desafioEDTime').show();
        $('#desafiolblEDType').show();
        $('#desafioEDType').show();
        $('#desafioENavigationButtons').hide();
        $('label[for=desafioECSolution], #desafioECSolution').hide();
        $('label[for=desafioECTitle], #desafioECTitle').hide();
        $('label[for=desafioEDTitle], #desafioEDTitle').show();
        $('label[for=desafioEDSolution], #desafioEDSolution').show();
        $('#desafioENumQuestionDiv').hide();
        $('#desafioEDTitle').val($exeDevice.desafioTitle);
        $('#desafioEDSolution').val($exeDevice.desafioSolution);
        $('#desafioEDTime').val($exeDevice.desafioTime);
        $('#desafioEDType').val($exeDevice.desafioType);
        $('#divDesafioEDescription').show();
        $("#desafioEChallenges").hide();
    },

}