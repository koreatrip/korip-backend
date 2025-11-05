// static/admin/js/place_dynamic_filtering.js
// 관광지 admin에서 카테고리/지역 실시간 필터링

(function() {
    // Django admin jQuery가 로드될 때까지 기다림
    if (typeof django === 'undefined' || typeof django.jQuery === 'undefined') {
        setTimeout(arguments.callee, 50);
        return;
    }

    var $ = django.jQuery;

    $(document).ready(function() {
        console.log("Place dynamic filtering loaded!");

    // ===== 카테고리 → 서브카테고리 필터링 =====
    var $categoryField = $("#id_category");
    var $subCategoryField = $("#id_sub_category");

    // 서브카테고리 원본 데이터 저장
    var allSubCategories = [];

    // 페이지 로드 시 모든 서브카테고리 저장
    $subCategoryField.find("option").each(function() {
        var $option = $(this);
        allSubCategories.push({
            value: $option.val(),
            text: $option.text(),
            parentId: $option.data("parent") || null
        });
    });

    // 카테고리 변경 이벤트
    $categoryField.on("change", function() {
        var selectedCategoryId = $(this).val();

        console.log("Category changed:", selectedCategoryId);

        // 서브카테고리 초기화
        $subCategoryField.empty();
        $subCategoryField.append('<option value="">---------</option>');

        if (!selectedCategoryId) {
            // 카테고리 선택 안 했으면 전체 목록
            $.each(allSubCategories, function(index, subCat) {
                if (subCat.value) {
                    $subCategoryField.append(
                        $("<option></option>")
                            .attr("value", subCat.value)
                            .text(subCat.text)
                    );
                }
            });
        } else {
            // AJAX로 서버에서 필터링된 데이터 가져오기
            $.ajax({
                url: "/admin/categories/subcategory/",
                data: {
                    parent: selectedCategoryId
                },
                success: function(data) {
                    if (data.results) {
                        $.each(data.results, function(index, item) {
                            $subCategoryField.append(
                                $("<option></option>")
                                    .attr("value", item.id)
                                    .text(item.text)
                            );
                        });
                    }
                },
                error: function() {
                    console.log("AJAX failed, using client-side filtering");
                    filterSubCategoriesLocally(selectedCategoryId);
                }
            });
        }
    });

    // 클라이언트 사이드 필터링 (AJAX 실패 시 백업)
    function filterSubCategoriesLocally(categoryId) {
        $.each(allSubCategories, function(index, subCat) {
            if (subCat.value) {
                $subCategoryField.append(
                    $("<option></option>")
                        .attr("value", subCat.value)
                        .text(subCat.text)
                );
            }
        });
    }


    // ===== 지역 → 지역구 필터링 =====
    var $regionField = $("#id_region");
    var $subRegionField = $("#id_sub_region");

    // 지역구 원본 데이터 저장
    var allSubRegions = [];

    $subRegionField.find("option").each(function() {
        var $option = $(this);
        allSubRegions.push({
            value: $option.val(),
            text: $option.text(),
            regionId: $option.data("region") || null
        });
    });

    // 지역 변경 이벤트
    $regionField.on("change", function() {
        var selectedRegionId = $(this).val();

        console.log("Region changed:", selectedRegionId);

        // 지역구 초기화
        $subRegionField.empty();
        $subRegionField.append('<option value="">---------</option>');

        if (!selectedRegionId) {
            // 지역 선택 안 했으면 전체 목록
            $.each(allSubRegions, function(index, subReg) {
                if (subReg.value) {
                    $subRegionField.append(
                        $("<option></option>")
                            .attr("value", subReg.value)
                            .text(subReg.text)
                    );
                }
            });
        } else {
            // AJAX로 서버에서 필터링된 데이터 가져오기
            $.ajax({
                url: "/admin/regions/subregion/",
                data: {
                    region: selectedRegionId
                },
                success: function(data) {
                    if (data.results) {
                        $.each(data.results, function(index, item) {
                            $subRegionField.append(
                                $("<option></option>")
                                    .attr("value", item.id)
                                    .text(item.text)
                            );
                        });
                    }
                },
                error: function() {
                    console.log("AJAX failed, using client-side filtering");
                    filterSubRegionsLocally(selectedRegionId);
                }
            });
        }
    });

    function filterSubRegionsLocally(regionId) {
        $.each(allSubRegions, function(index, subReg) {
            if (subReg.value) {
                $subRegionField.append(
                    $("<option></option>")
                        .attr("value", subReg.value)
                        .text(subReg.text)
                );
            }
        });
    }

    });  // $(document).ready 닫기

})();  // 즉시 실행 함수 닫기
